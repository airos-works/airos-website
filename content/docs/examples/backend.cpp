// backend.cpp: the smallest back end. It claims the float32 RELU operators
// of a network and runs stretches of them in its own "program", which here
// is plain C++ standing in for a device. A real back end opens its driver
// under /dev/npu in CountDevices(), converts and uploads weights in
// CreateProgram() and submits jobs in Run().
//
// Build: g++ -shared -fPIC backend.cpp -o example.neural -lneural -lbe
// Install: ~/config/non-packaged/add-ons/neural/example.neural, then
//   neural devices        lists "example/0"
//   neural compare model.tflite -d example/0

#include <map>
#include <new>
#include <set>
#include <string.h>
#include <vector>

#include <Message.h>
#include <add-ons/neural/NeuralBackend.h>


static bool
is_float_relu(const BNeuralGraph& graph, const neural_graph_operator* op)
{
	if (op->code != B_NEURAL_OP_RELU || op->input_count != 1
		|| op->output_count != 1) {
		return false;
	}
	const neural_graph_tensor* in = graph.TensorAt(op->inputs[0]);
	const neural_graph_tensor* out = graph.TensorAt(op->outputs[0]);
	return in->type == B_NEURAL_FLOAT32 && out->type == B_NEURAL_FLOAT32;
}


static size_t
element_count(const neural_graph_tensor* tensor)
{
	size_t count = 1;
	for (int32 i = 0; i < tensor->rank; i++)
		count *= tensor->dimensions[i];
	return count;
}


class ExampleProgram : public BNeuralProgram {
public:
	ExampleProgram(const BNeuralGraph& graph,
		const neural_partition& partition)
		:
		fGraph(graph),
		fOperators(partition.operators,
			partition.operators + partition.operator_count)
	{
		// The kit promises memory only for the tensors that cross the
		// stretch's edges; what is made and used inside is the back end's
		// own (a device keeps it in its memory).
		std::set<int32> edges(partition.inputs,
			partition.inputs + partition.input_count);
		edges.insert(partition.outputs,
			partition.outputs + partition.output_count);
		for (int32 index : fOperators) {
			int32 output = graph.OperatorAt(index)->outputs[0];
			if (edges.count(output) == 0) {
				fScratch[output].resize(
					element_count(graph.TensorAt(output)));
			}
		}
	}

	// tensors[] has one entry per tensor of the graph; the partition's
	// inputs are filled in, its outputs are to be written.
	virtual status_t Run(void* const* tensors)
	{
		for (int32 index : fOperators) {
			const neural_graph_operator* op = fGraph.OperatorAt(index);
			const float* in = _Memory(tensors, op->inputs[0]);
			float* out = _Memory(tensors, op->outputs[0]);
			if (in == NULL || out == NULL)
				return B_BAD_VALUE;
				// the kit runs this stretch on the CPU this time

			size_t count = element_count(fGraph.TensorAt(op->outputs[0]));
			for (size_t i = 0; i < count; i++)
				out[i] = in[i] > 0 ? in[i] : 0;
		}
		return B_OK;
	}

private:
	float* _Memory(void* const* tensors, int32 index)
	{
		auto scratch = fScratch.find(index);
		if (scratch != fScratch.end())
			return scratch->second.data();
		return (float*)tensors[index];
	}

	const BNeuralGraph&					fGraph;
	std::vector<int32>					fOperators;
	std::map<int32, std::vector<float>>	fScratch;
};


class ExampleBackend : public BNeuralBackend {
public:
	ExampleBackend(image_id image)
		:
		BNeuralBackend(image)
	{
	}

	virtual const char* Name() const
	{
		return "example";
	}

	virtual int32 CountDevices()
	{
		// Look for the hardware here; 0 costs nothing more.
		return 1;
	}

	virtual status_t GetDeviceInfo(int32 device, neural_device_info* info,
		BMessage* details)
	{
		if (device != 0)
			return B_BAD_INDEX;
		memset(info, 0, sizeof(*info));
		strlcpy(info->id, "0", sizeof(info->id));
		strlcpy(info->name, "Example accelerator", sizeof(info->name));
		strlcpy(info->vendor, "Example", sizeof(info->vendor));
		info->kind = B_NEURAL_DEVICE_NPU;
		info->flags = B_NEURAL_DEVICE_FLOAT;
		info->priority = 10;
		if (details != NULL)
			details->AddString("driver", "none");
		return B_OK;
	}

	// Asked before anything is loaded, also just to choose a device: look
	// at codes, types, shapes and parameters only, and say yes only to what
	// the device computes correctly.
	virtual status_t GetSupportedOperators(int32 device,
		const BNeuralGraph& graph, bool* supported)
	{
		for (int32 i = 0; i < graph.CountOperators(); i++)
			supported[i] = is_float_relu(graph, graph.OperatorAt(i));
		return B_OK;
	}

	// One call per stretch of supported operators: convert and upload
	// weights here. An error means "run this stretch on the CPU". The
	// graph outlives the program; the partition is copied.
	virtual status_t CreateProgram(int32 device, const BNeuralGraph& graph,
		const neural_partition& partition, uint32 flags,
		BNeuralProgram** _program)
	{
		ExampleProgram* program
			= new(std::nothrow) ExampleProgram(graph, partition);
		if (program == NULL)
			return B_NO_MEMORY;
		*_program = program;
		return B_OK;
	}
};


extern "C" _EXPORT BNeuralBackend*
instantiate_neural_backend(image_id image)
{
	return new(std::nothrow) ExampleBackend(image);
}
