// detect.cpp: what a detection model finds in a picture, and where.
//
//   detect ssd_mobilenet_v1_quant.tflite ssd_mobilenet_v1_quant.txt street.jpg
//
// Build: g++ detect.cpp -o detect -lneural -lbe -ltranslation

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

	BApplication app("application/x-vnd.example-detect");

	BNeuralModel model(argv[1]);
	BNeuralSession session(model);
	if (session.InitCheck() != B_OK) {
		fprintf(stderr, "%s: %s %s\n", argv[1],
			neural_error_string(session.InitCheck()), model.ErrorDetails());
		return 1;
	}
	if (!BNeuralUtils::IsDetector(session)) {
		fprintf(stderr, "%s is not a detection model\n", argv[1]);
		return 1;
	}

	BBitmap* picture = BTranslationUtils::GetBitmap(argv[3]);
	if (picture == NULL) {
		fprintf(stderr, "%s: not a picture\n", argv[3]);
		return 1;
	}

	// The mapping remembers where the picture went in the tensor, to take
	// the model's boxes (fractions of its input) back to the picture.
	neural_image_mapping mapping;
	status_t status = BNeuralUtils::SetTensorFromBitmap(session.InputAt(0),
		picture, NULL, NULL, &mapping);
	delete picture;
	if (status == B_OK)
		status = session.Run();
	if (status != B_OK) {
		fprintf(stderr, "run: %s\n", neural_error_string(status));
		return 1;
	}

	BStringList labels;
	BNeuralUtils::GetLabels(argv[2], &labels);

	neural_detection found[32];
	int32 count = BNeuralUtils::GetDetections(session, found, 32);
	for (int32 i = 0; i < count; i++) {
		if (found[i].score < 0.4f)
			continue;

		BRect box = mapping.ToBitmap(found[i].left, found[i].top,
			found[i].right, found[i].bottom);
		// Detection label files begin with a line for "nothing".
		printf("%3.0f%%  %-16s at %.0f, %.0f, %.0f × %.0f pixels\n",
			found[i].score * 100,
			labels.StringAt(found[i].class_index + 1).String(),
			box.left, box.top, box.Width(), box.Height());
	}
	return 0;
}
