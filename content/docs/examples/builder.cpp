// builder.cpp: a network made in code, y = min(max(x * 2 + 1, 0), 6), run on
// the CPU (the reference) and on the device the kit chooses, and compared.
// This is also how a back end is tested: one operator at a time against
// the CPU.
//
// Build: g++ builder.cpp -o builder -lneural -lbe

#include <math.h>
#include <stdio.h>

#include <NeuralKit.h>


static status_t
build(BNeuralModel* model)
{
	BNeuralModelBuilder builder("scale and clamp");

	int32 shape[] = { 1, 8 };
	int32 one[] = { 1 };
	int32 x = builder.AddInput(BTensorInfo(B_NEURAL_FLOAT32, 2, shape, "x"));

	float two = 2.0f;
	int32 factor = builder.AddConstant(
		BTensorInfo(B_NEURAL_FLOAT32, 1, one, "two"), &two, sizeof(two));
	float oneValue = 1.0f;
	int32 offset = builder.AddConstant(
		BTensorInfo(B_NEURAL_FLOAT32, 1, one, "one"), &oneValue,
		sizeof(oneValue));

	// Binary operators broadcast and take neural_binary_params; the
	// clamp to 0 .. 6 is fused into the ADD as its activation.
	neural_binary_params none = { B_NEURAL_ACTIVATION_NONE };
	int32 inputs[2] = { x, factor };
	int32 scaled = builder.AddOperator(B_NEURAL_OP_MUL, inputs, 2,
		BTensorInfo(B_NEURAL_FLOAT32, 2, shape, "scaled"), &none,
		sizeof(none));

	neural_binary_params relu6 = { B_NEURAL_ACTIVATION_RELU6 };
	inputs[0] = scaled;
	inputs[1] = offset;
	int32 y = builder.AddOperator(B_NEURAL_OP_ADD, inputs, 2,
		BTensorInfo(B_NEURAL_FLOAT32, 2, shape, "y"), &relu6, sizeof(relu6));

	builder.MarkOutput(y);
	// Checks types, shapes and order; an error of any Add...() above comes
	// back here.
	return builder.Build(model);
}


static status_t
run(BNeuralSession& session, const float* input, float* output)
{
	session.InputAt(0)->SetValues(input, 8);
	status_t status = session.Run();
	if (status == B_OK)
		status = session.OutputAt(0)->GetValues(output, 8);
	return status;
}


int
main()
{
	BNeuralModel model;
	status_t status = build(&model);
	if (status != B_OK) {
		fprintf(stderr, "build: %s\n", neural_error_string(status));
		return 1;
	}

	BNeuralSession reference(model, B_NEURAL_CPU_ONLY);
	BNeuralSession session(model);
	if (reference.InitCheck() != B_OK || session.InitCheck() != B_OK) {
		fprintf(stderr, "no session\n");
		return 1;
	}

	float input[8] = { -3, -1, -0.5f, 0, 0.5f, 1, 2.5f, 4 };
	float expected[8];
	float actual[8];
	if (run(reference, input, expected) != B_OK
		|| run(session, input, actual) != B_OK) {
		fprintf(stderr, "run failed\n");
		return 1;
	}

	float worst = 0;
	for (int i = 0; i < 8; i++) {
		printf("%5.1f -> %4.1f\n", input[i], actual[i]);
		worst = fmaxf(worst, fabsf(actual[i] - expected[i]));
	}
	printf("%s against the CPU: largest difference %g\n",
		session.Device().ID(), worst);
	return 0;
}
