// devices.cpp: the machine's devices, how much of a model each would run,
// and the device the kit would choose.
//
//   devices mobilenet_v2_1.0_224.tflite
//
// Build: g++ devices.cpp -o devices -lneural -lbe

#include <stdio.h>

#include <Message.h>
#include <NeuralKit.h>


static void
print_choice(const char* what, const BNeuralModel& model, uint32 flags)
{
	BNeuralDevice device;
	status_t status = BNeuralRoster::Default()->GetDefaultDevice(&device,
		flags, &model);
	if (status == B_OK)
		printf("%-28s %s\n", what, device.ID());
	else
		printf("%-28s none (%s)\n", what, neural_error_string(status));
}


int
main(int argc, char** argv)
{
	if (argc != 2) {
		fprintf(stderr, "usage: %s <model>\n", argv[0]);
		return 2;
	}

	BNeuralModel model(argv[1]);
	if (model.InitCheck() != B_OK) {
		fprintf(stderr, "%s: %s %s\n", argv[1],
			neural_error_string(model.InitCheck()), model.ErrorDetails());
		return 1;
	}

	// Asking the roster anything loads the back-end add-ons; one whose
	// hardware is not in this machine reports no devices.
	BNeuralRoster* roster = BNeuralRoster::Default();
	for (int32 i = 0; i < roster->CountDevices(); i++) {
		BNeuralDevice device;
		if (roster->GetDeviceAt(i, &device) != B_OK)
			continue;

		uint32 flags = device.Flags();
		const char* types = (flags & B_NEURAL_DEVICE_QUANTIZED) == 0 ? "float"
			: (flags & B_NEURAL_DEVICE_FLOAT) == 0 ? "quantized"
			: "quantized and float";
		printf("%-14s %s %s: %s networks, back end %s\n", device.ID(),
			neural_device_kind_name(device.Kind()), device.Name(), types,
			device.Backend());

		// Asks the back end only; nothing is loaded onto the device.
		printf("               runs %d of the model's %d operators\n",
			(int)device.CountSupportedOperators(model),
			(int)model.CountOperators());

		BMessage info;
		if (device.GetInfo(&info) == B_OK)
			info.PrintToStream();
	}

	print_choice("fastest:", model, B_NEURAL_PREFER_SPEED);
	print_choice("least power:", model, B_NEURAL_PREFER_LOW_POWER);
	print_choice("whole model on the device:", model, B_NEURAL_NO_FALLBACK);
	return 0;
}
