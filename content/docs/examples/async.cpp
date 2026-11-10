// async.cpp: runs without blocking. A looper owns the session and starts
// each run with RunAsync(); frames that arrive while a run is going on
// replace each other, and the newest is taken when the run is over. This is
// how Lookout keeps up with a camera.
//
//   async mobilenet_v1_1.0_224_quant.tflite a.jpg b.jpg c.jpg
//
// Build: g++ async.cpp -o async -lneural -lbe -ltranslation

#include <stdio.h>

#include <Application.h>
#include <Bitmap.h>
#include <Looper.h>
#include <NeuralKit.h>
#include <TranslationUtils.h>


enum {
	kMsgFrame = 'fram',		// "bitmap" (pointer): a new picture to look at
	kMsgRunDone = 'done',	// our own completion message
	kMsgNoMore = 'nomo'		// quit the application when all is done
};


class Classifier : public BLooper {
public:
	Classifier(const BNeuralModel& model)
		:
		BLooper("classifier"),
		fSession(model),
		fRunning(false),
		fDone(false),
		fNext(NULL)
	{
	}

	~Classifier()
	{
		// The session's destructor waits for a run that is going on.
		delete fNext;
	}

	status_t InitCheck() const { return fSession.InitCheck(); }

	virtual void MessageReceived(BMessage* message)
	{
		switch (message->what) {
			case kMsgFrame:
			{
				BBitmap* bitmap;
				if (message->FindPointer("bitmap", (void**)&bitmap) != B_OK)
					break;
				// Only the newest frame waits; older ones are dropped.
				delete fNext;
				fNext = bitmap;
				if (!fRunning)
					_StartNext();
				_QuitWhenDone();
				break;
			}

			case kMsgRunDone:
			{
				fRunning = false;
				status_t status = message->GetInt32("neural:status", B_ERROR);
				if (status == B_OK) {
					const BTensor* output = fSession.OutputAt(0);
					int64 best = output->IndexOfMaximum();
					printf("class %d (%.0f%%) in %.1f ms on %s\n", (int)best,
						output->ValueAt(best) * 100,
						message->GetInt64("neural:duration", 0) / 1000.0,
						fSession.Device().ID());
				} else
					printf("run failed: %s\n", neural_error_string(status));

				if (fNext != NULL)
					_StartNext();
				_QuitWhenDone();
				break;
			}

			case kMsgNoMore:
				fDone = true;
				_QuitWhenDone();
				break;

			default:
				BLooper::MessageReceived(message);
		}
	}

private:
	void _QuitWhenDone()
	{
		if (fDone && !fRunning && fNext == NULL)
			be_app->PostMessage(B_QUIT_REQUESTED);
	}

	void _StartNext()
	{
		BBitmap* bitmap = fNext;
		fNext = NULL;
		status_t status = BNeuralUtils::SetTensorFromBitmap(
			fSession.InputAt(0), bitmap);
		delete bitmap;

		// Returns at once; kMsgRunDone comes back with "neural:status",
		// "neural:duration" and the other neural: fields added. Inputs
		// and outputs are not to be touched until then.
		BMessage done(kMsgRunDone);
		if (status == B_OK)
			status = fSession.RunAsync(BMessenger(this), &done);
		if (status == B_OK)
			fRunning = true;
		else
			printf("cannot run: %s\n", neural_error_string(status));
	}

	BNeuralSession	fSession;
	bool			fRunning;
	bool			fDone;
	BBitmap*		fNext;
};


int
main(int argc, char** argv)
{
	if (argc < 3) {
		fprintf(stderr, "usage: %s <model> <picture>...\n", argv[0]);
		return 2;
	}

	BApplication app("application/x-vnd.example-async");

	BNeuralModel model(argv[1]);
	Classifier* classifier = new Classifier(model);
	if (classifier->InitCheck() != B_OK) {
		fprintf(stderr, "%s: %s\n", argv[1],
			neural_error_string(classifier->InitCheck()));
		delete classifier;
		return 1;
	}
	classifier->Run();

	for (int i = 2; i < argc; i++) {
		BBitmap* bitmap = BTranslationUtils::GetBitmap(argv[i]);
		if (bitmap == NULL)
			continue;
		BMessage frame(kMsgFrame);
		frame.AddPointer("bitmap", bitmap);
		classifier->PostMessage(&frame);
	}
	classifier->PostMessage(kMsgNoMore);

	app.Run();

	classifier->Lock();
	classifier->Quit();
	return 0;
}
