// transcribe.cpp: speech to text, fed as a recording would be. The audio
// file is decoded with the Media Kit and handed to the recognizer buffer by
// buffer; the text comes back as messages to a looper. Feeding from a
// microphone works the same way, from the thread that records.
//
//   transcribe speech.wav [model]
//
// The model is a name ("whisper-tiny.en") or a model directory; without
// one, the first speech model installed in neural/models of a data
// directory, for example ~/config/non-packaged/data/neural/models/
// whisper-tiny.en (see fetch-models.sh). Build: g++ transcribe.cpp -o transcribe -lneural -lmedia -lbe

#include <stdio.h>
#include <stdlib.h>

#include <Entry.h>
#include <Looper.h>
#include <MediaFile.h>
#include <MediaTrack.h>
#include <NeuralKit.h>


class Printer : public BLooper {
public:
	Printer()
		:
		BLooper("printer"),
		fFinished(create_sem(0, "finished")),
		fStatus(B_OK)
	{
	}

	~Printer()
	{
		delete_sem(fFinished);
	}

	virtual void MessageReceived(BMessage* message)
	{
		switch (message->what) {
			case B_SPEECH_RESULT:
				// A result that is not final is the recognizer's reading,
				// so far, of everything after the last final phrase: it
				// replaces the one before. Here only final ones are shown.
				if (message->GetBool("speech:final", false)) {
					printf("[%6.2f – %6.2f]  %s\n",
						message->GetInt64("speech:start", 0) / 1e6,
						message->GetInt64("speech:end", 0) / 1e6,
						message->GetString("speech:text", ""));
				}
				break;

			case B_SPEECH_FINISHED:
				// After the last result of the recording.
				fStatus = message->GetInt32("speech:status", B_ERROR);
				printf("%.1f s of audio in %.1f s\n",
					message->GetInt64("speech:audio", 0) / 1e6,
					message->GetInt64("speech:duration", 0) / 1e6);
				release_sem(fFinished);
				break;

			default:
				BLooper::MessageReceived(message);
		}
	}

	status_t WaitForEnd()
	{
		acquire_sem(fFinished);
		return fStatus;
	}

private:
	sem_id		fFinished;
	status_t	fStatus;
};


static status_t
feed_file(BSpeechRecognizer& recognizer, const char* path)
{
	entry_ref ref;
	status_t status = get_ref_for_path(path, &ref);
	if (status != B_OK)
		return status;

	BMediaFile file(&ref);
	if ((status = file.InitCheck()) != B_OK)
		return status;

	for (int32 i = 0; i < file.CountTracks(); i++) {
		BMediaTrack* track = file.TrackAt(i);
		media_format format;
		format.Clear();
		format.type = B_MEDIA_RAW_AUDIO;
		format.u.raw_audio = media_raw_audio_format::wildcard;
		if (track->DecodedFormat(&format) != B_OK
			|| format.type != B_MEDIA_RAW_AUDIO) {
			file.ReleaseTrack(track);
			continue;
		}

		// Any raw format will do: the recognizer makes 16 kHz mono of it.
		const media_raw_audio_format& raw = format.u.raw_audio;
		size_t frameSize = (raw.format & media_raw_audio_format
			::B_AUDIO_SIZE_MASK) * raw.channel_count;
		char* buffer = NULL;
		if (frameSize > 0 && raw.buffer_size >= frameSize)
			buffer = (char*)malloc(raw.buffer_size);
		status = buffer != NULL ? recognizer.Start(&raw) : B_NO_MEMORY;

		int64 frames;
		while (status == B_OK && track->ReadFrames(buffer, &frames) == B_OK
			&& frames > 0) {
			// Returns at once; B_BUSY only when ten minutes of audio are
			// waiting for the model.
			while ((status = recognizer.Feed(buffer, frames * frameSize))
					== B_BUSY)
				snooze(50000);
		}
		free(buffer);
		file.ReleaseTrack(track);
		return status;
	}
	return B_MEDIA_NO_HANDLER;
}


int
main(int argc, char** argv)
{
	if (argc != 2 && argc != 3) {
		fprintf(stderr, "usage: %s <audio file> [model]\n", argv[0]);
		return 2;
	}

	// NULL: the first speech model installed. The device is chosen as for
	// a BNeuralSession.
	BSpeechRecognizer recognizer;
	status_t status = recognizer.SetTo(argc == 3 ? argv[2] : NULL);
	if (status != B_OK) {
		fprintf(stderr, "no recognizer: %s (%s)\n",
			neural_error_string(status), recognizer.ErrorDetails());
		return 1;
	}
	printf("model %s on %s\n", recognizer.ModelName(),
		recognizer.Device().ID());

	Printer* printer = new Printer();
	printer->Run();
	recognizer.SetTarget(BMessenger(printer));

	status = feed_file(recognizer, argv[1]);
	if (status == B_OK) {
		// The rest is recognized, then B_SPEECH_FINISHED is sent.
		recognizer.Finish();
		status = printer->WaitForEnd();
	} else
		recognizer.Cancel();

	printer->Lock();
	printer->Quit();

	if (status != B_OK) {
		fprintf(stderr, "%s: %s\n", argv[1], neural_error_string(status));
		return 1;
	}
	return 0;
}
