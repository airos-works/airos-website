// classify.cpp: the five best classes of a picture.
//
//   classify mobilenet_v1_1.0_224_quant.tflite labels.txt cat.jpg
//
// Build: g++ classify.cpp -o classify -lneural -lbe -ltranslation

#include <stdio.h>

#include <Application.h>
#include <Bitmap.h>
#include <NeuralKit.h>
#include <StringList.h>
#include <TranslationUtils.h>


int
main(int argc, char** argv)
{
	if (argc != 4) {
		fprintf(stderr, "usage: %s <model> <labels> <picture>\n", argv[0]);
		return 2;
	}

	// The Translation Kit makes bitmaps, and bitmaps need an application.
	BApplication app("application/x-vnd.example-classify");

	BNeuralModel model(argv[1]);
	if (model.InitCheck() != B_OK) {
		fprintf(stderr, "%s: %s %s\n", argv[1],
			neural_error_string(model.InitCheck()), model.ErrorDetails());
		return 1;
	}

	// The slow part: the kit picks a device (an NPU, else a GPU, else the
	// CPU) and the device's back end uploads the weights.
	BNeuralSession session(model);
	if (session.InitCheck() != B_OK) {
		fprintf(stderr, "no session: %s\n",
			neural_error_string(session.InitCheck()));
		return 1;
	}

	BBitmap* picture = BTranslationUtils::GetBitmap(argv[3]);
	if (picture == NULL) {
		fprintf(stderr, "%s: not a picture\n", argv[3]);
		return 1;
	}

	// Scales the picture into the input tensor, whatever its size and
	// element type (uint8, int8 or float).
	neural_image_options options;
	options.fit = B_NEURAL_FIT_STRETCH;
	status_t status = BNeuralUtils::SetTensorFromBitmap(session.InputAt(0),
		picture, NULL, &options);
	delete picture;
	if (status == B_OK)
		status = session.Run();
	if (status != B_OK) {
		fprintf(stderr, "run: %s\n", neural_error_string(status));
		return 1;
	}

	BStringList labels;
	BNeuralUtils::GetLabels(argv[2], &labels);

	int64 indices[5];
	float scores[5];
	int32 count = BNeuralUtils::GetTopValues(*session.OutputAt(0), 5,
		indices, scores);
	for (int32 i = 0; i < count; i++) {
		printf("%5.1f%%  %s\n", scores[i] * 100,
			labels.StringAt(indices[i]).String());
	}

	neural_run_info info;
	session.GetRunInfo(&info);
	printf("on %s (%s): %d operators on the device, %d on the CPU, "
		"%.1f ms\n", session.Device().Name(), session.Device().ID(),
		(int)info.device_operators, (int)info.cpu_operators,
		info.last_duration / 1000.0);
	return 0;
}
