"""Developer documentation: how air/OS's APIs differ from Haiku's, kit by kit,
and the Neural Kit in full (guide, reference, examples).

Content lives in content/docs/: kits.json (the differences), neural-api.json
(the Neural Kit reference) and examples/ (programs and the output they gave
on hardware). build.py calls build() with its page helpers."""
from html import escape as e
import json
import re

# Haiku's own reference; these pages only document what air/OS changes.
HAIKU_BOOK = 'https://www.haiku-os.org/docs/api/'
BE_BOOK = 'https://www.haiku-os.org/legacy-docs/bebook/'
HAIKU_DEV = 'https://www.haiku-os.org/development/'

SECTIONS = [
    ('docs/', 'Overview'),
    ('docs/kits/', 'Kit differences'),
    ('docs/neural/', 'Neural Kit'),
    ('docs/neural/reference/', 'Neural Kit reference'),
    ('docs/neural/examples/', 'Neural Kit examples'),
]


class Site:
    def __init__(self, page, url, link, intro, root, github):
        self.page, self.url, self.link, self.intro = page, url, link, intro
        self.root, self.github = root, github
        self.kits = json.loads((root / 'content/docs/kits.json').read_text())
        self.api = json.loads((root / 'content/docs/neural-api.json').read_text())
        self.commit = self.kits['source']['commit']

    # Links into the airos-works/haiku repository, pinned to the reviewed commit.
    def source(self, path, label=None):
        return self.link(f'{self.github}/haiku/blob/{self.commit}/{path}', label or e(path) + ' ↗')

    def design(self, name):
        return self.source('docs/airos/' + name, 'Design notes: ' + e(name) + ' ↗')

    def commit_link(self, sha):
        return f'<a class="sha" href="{self.github}/haiku/commit/{sha}">{sha[:10]}</a>'

    def inline(self, text):
        """Escapes text, then turns `code`, **bold** and [label](href) into HTML."""
        out = e(text, quote=False)
        out = re.sub(r'`([^`]+)`', r'<code>\1</code>', out)
        out = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', out)
        def repl(m):
            href = m.group(2)
            if href.startswith('docs/'):
                href = self.url(href)
            return f'<a href="{e(href, quote=True)}">{m.group(1)}</a>'
        return re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', repl, out)


def pre(code, cls=''):
    return f'<pre{" class=" + chr(34) + cls + chr(34) if cls else ""}><code>{e(code.strip(chr(10)))}</code></pre>'


def diff(text):
    lines = []
    for line in text.split('\n'):
        kind = {'+': 'add', '-': 'del'}.get(line[:1])
        # Tab stops as in the headers, counted after the two-column marker.
        body = e(line[:2] + line[2:].expandtabs(4))
        lines.append(f'<span class="{kind}">{body}</span>' if kind else body)
    return '<pre class="diff"><code>' + '\n'.join(lines) + '</code></pre>'


def table(head, rows):
    th = ''.join(f'<th scope="col">{h}</th>' for h in head)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>' for row in rows)
    return f'<div class="table-wrap"><table class="doc-table"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def doc_page(s, path, title, description, kicker, heading, lead, toc, body):
    tabs = ''.join(s.link(s.url(p), label, 'active' if p == path else '') for p, label in SECTIONS)
    nav = f'<nav class="doc-tabs" aria-label="Documentation">{tabs}</nav>'
    side = ''
    if toc:
        items = ''.join(f'<li><a href="#{anchor}">{label}</a></li>' for anchor, label in toc)
        side = f'<nav class="doc-toc" aria-label="On this page"><p class="eyebrow">On this page</p><ul>{items}</ul></nav>'
    html = s.intro(kicker, heading, lead, wide=True) + nav
    html += f'<div class="doc-layout{" no-toc" if not toc else ""}">{side}<div class="doc-body">{body}</div></div>'
    s.page(path, title, description, html)


# ---------------------------------------------------------------- overview

def overview(s):
    k = s.kits
    counts = lambda kit, kind: sum(1 for c in kit['changes'] if c['kind'] == kind)
    body = '<section id="start"><h2>Start with Haiku’s reference</h2>'
    body += '<p>air/OS is built on Haiku, and Haiku’s documentation describes almost all of its API. These pages do not repeat it. They cover what the fork adds or changes, kit by kit, and document in full the one kit that is new: the Neural Kit.</p>'
    body += '<div class="doc-cards">'
    body += f'<a class="doc-card" href="{HAIKU_BOOK}"><span class="tag">Haiku</span><strong>The Haiku Book ↗</strong><span>Haiku’s API reference, kit by kit. The reference for everything not listed here.</span></a>'
    body += f'<a class="doc-card" href="{BE_BOOK}"><span class="tag">Haiku</span><strong>The Be Book ↗</strong><span>The original BeOS documentation, still the best introduction to many classes.</span></a>'
    body += f'<a class="doc-card" href="{HAIKU_DEV}"><span class="tag">Haiku</span><strong>Developing for Haiku ↗</strong><span>Tools, tutorials and the developer community.</span></a>'
    body += '</div></section>'

    body += '<section id="new"><h2>What air/OS adds</h2><div class="doc-cards two">'
    body += f'<a class="doc-card feature" href="{s.url("docs/neural/")}"><span class="tag">New kit</span><strong>Neural Kit</strong><span>Run neural networks on NPUs, graphics processors and the CPU through one API, and turn speech into text on the machine itself.</span><em>Guide, reference and examples →</em></a>'
    total = sum(len(kit['changes']) for kit in k['kits'])
    body += f'<a class="doc-card feature" href="{s.url("docs/kits/")}"><span class="tag">{total} changes</span><strong>Kit differences</strong><span>Every public API the fork adds or changes, shown as a diff against Haiku, plus behaviour changes and the private APIs system apps use.</span><em>Kit by kit →</em></a>'
    body += '</div></section>'

    body += '<section id="kits"><h2>Kit by kit</h2>'
    rows = []
    for kit in k['kits']:
        marks = ' '.join(f'<span class="kind kind-{kind}">{counts(kit, kind)} {label.lower()}</span>'
                         for kind, (label, _) in k['kinds'].items() if counts(kit, kind))
        rows.append([s.link(s.url('docs/kits/#' + kit['id']), e(kit['name'])), e(kit['summary']), marks])
    rows.append([s.link(s.url('docs/neural/'), 'Neural Kit'), 'New in air/OS: inference on NPUs, GPUs and the CPU, and speech recognition.', '<span class="kind kind-new">new kit</span>'])
    body += table(['Kit', 'What changed', 'Changes'], rows)
    unchanged = ', '.join(s.link(href, e(name)) for name, href in k['unchanged'])
    body += f'<p class="meta">No API changes: {unchanged}.</p></section>'

    body += '<section id="compatibility"><h2>Compatibility</h2>'
    body += '<ul class="checks">'
    body += '<li><strong>Apps built for Haiku run on air/OS unchanged.</strong> No class gained a virtual function or changed size; new structure fields use reserved space.</li>'
    body += '<li><strong>Apps that use these additions need air/OS.</strong> air/OS defines no compiler macro of its own. A kit that is new can be detected with <code>__has_include(&lt;NeuralKit.h&gt;)</code>; additions to existing classes cannot, so build such apps for air/OS, as Summit ships separate builds for air/OS and stock Haiku.</li>'
    body += '<li><strong>Private headers may change.</strong> APIs marked Private are what the system’s own apps use. They are listed so you know they exist; there is no promise they stay as they are.</li>'
    body += '<li><strong>Headers and libraries</strong> come with the system’s development package, as on Haiku: the headers in <code>/boot/system/develop/headers</code>, the libraries to link with in <code>/boot/system/develop/lib</code>.</li>'
    body += '</ul></section>'

    b = k['baseline']
    body += f'<p class="meta">Compared with Haiku at {s.commit_link(b["commit"])} ({e(b["hrev"])}, {e(b["date"])}), the upstream commit air/OS master is based on, and air/OS master at {s.commit_link(s.commit)} ({e(k["source"]["date"])}). Reviewed {e(k["reviewed"])}.</p>'
    toc = [('start', 'Haiku’s reference'), ('new', 'What air/OS adds'), ('kits', 'Kit by kit'), ('compatibility', 'Compatibility')]
    doc_page(s, 'docs/', 'Documentation', 'Developer documentation for air/OS: where its APIs differ from Haiku’s, kit by kit, and the new Neural Kit for NPUs.',
             'Documentation', 'Haiku’s API, and what air/OS adds.',
             'Write native apps for air/OS with Haiku’s API. These pages show where the fork differs from Haiku, kit by kit, with links back to Haiku’s own reference. The new Neural Kit is covered in full.', toc, body)


# ---------------------------------------------------------------- kit differences

def kit_differences(s):
    k = s.kits
    legend = ''.join(f'<li><span class="kind kind-{kind}">{label}</span> {e(text)}</li>' for kind, (label, text) in k['kinds'].items())
    b = k['baseline']
    body = f'<aside class="note"><strong>How to read this page.</strong> Each change shows its header and, for declarations, a diff against Haiku: lines marked + are new in air/OS, lines marked − are Haiku’s. Unmarked lines are unchanged context. The base is Haiku {s.commit_link(b["commit"])} ({e(b["hrev"])}). Every entry links to the commits that made it.<ul class="legend">{legend}</ul></aside>'
    for kit in k['kits']:
        refs = ''.join(s.link(href, e(label) + ' ↗', 'text-link') for label, href in kit['haiku'])
        body += f'<section class="kit" id="{kit["id"]}"><div class="kit-head"><h2>{e(kit["name"])}</h2><span>{e(kit["library"])}</span></div>'
        body += f'<p class="section-lead">{e(kit["summary"])}</p><div class="device-links">{refs}</div>'
        for change in kit['changes']:
            label = k['kinds'][change['kind']][0]
            anchor = kit['id'] + '-' + slug(change['title'])
            body += f'<article class="api-change" id="{anchor}"><div class="api-change-head"><span class="kind kind-{change["kind"]}">{label}</span><h3>{s.inline(change["title"])}</h3></div>'
            meta = f'<code>{e(change["header"])}</code>'
            if change.get('ref'):
                meta += s.link(change['ref'], 'Haiku reference ↗')
            body += f'<p class="api-meta">{meta}</p>'
            if change.get('diff'):
                body += diff(change['diff'])
            body += f'<p>{s.inline(change["text"])}</p><p class="api-links">'
            for key in ('doc', 'doc2'):
                if change.get(key):
                    body += s.design(change[key])
            body += '<span>' + ' '.join(s.commit_link(c) for c in change['commits']) + '</span></p></article>'
        body += '</section>'
    body += '<section class="kit" id="neural"><div class="kit-head"><h2>Neural Kit</h2><span>libneural.so</span></div>'
    body += f'<p class="section-lead">New in air/OS. See the {s.link(s.url("docs/neural/"), "Neural Kit guide")}, its {s.link(s.url("docs/neural/reference/"), "reference")} and {s.link(s.url("docs/neural/examples/"), "examples")}.</p></section>'
    unchanged = ', '.join(s.link(href, e(name)) for name, href in k['unchanged'])
    body += f'<section class="kit" id="unchanged"><div class="kit-head"><h2>Unchanged</h2></div><p class="section-lead">No API changes in the {unchanged}. Use Haiku’s documentation as it is.</p></section>'
    body += f'<p class="meta">Reviewed {e(k["reviewed"])} against air/OS master {s.commit_link(s.commit)}. Public headers were compared in full; behaviour changes and private APIs were selected for what an app developer can notice. Small internal fixes are left out and are in the {s.link(s.url("changelog/"), "changelog")}.</p>'
    toc = [(kit['id'], e(kit['name'])) for kit in k['kits']] + [('neural', 'Neural Kit'), ('unchanged', 'Unchanged kits')]
    doc_page(s, 'docs/kits/', 'Kit differences', 'How each kit of the air/OS API differs from Haiku’s: new and changed declarations as diffs, behaviour changes, and private APIs.',
             'Documentation · Kit differences', 'What changed, kit by kit.',
             'Every public header air/OS changes, shown as a diff against Haiku, with what it is for and the commits behind it. Behaviour changes in unchanged APIs, and the private APIs the system’s apps use, are listed alongside.', toc, body)


# ---------------------------------------------------------------- Neural Kit guide

def neural_guide(s):
    ref = lambda name, label=None: s.link(s.url('docs/neural/reference/#' + name), label or f'<code>{e(name)}</code>')
    ex = lambda anchor, label: s.link(s.url('docs/neural/examples/#' + anchor), label)
    body = '<section id="overview"><h2>Overview</h2>'
    body += '<p>The Neural Kit runs neural networks on the processors a machine has for them: neural processing units (NPUs), graphics processors and the CPU. A program hands the kit a model file and gets answers. Which processor computed them is the kit’s business, and the answers are the same on all of them: whatever a device cannot do, the CPU does.</p>'
    body += '<p>It is a kit like Haiku’s others: a library, <code>libneural.so</code>; public headers, <code>&lt;NeuralKit.h&gt;</code>; back-end add-ons for each kind of hardware in <code>add-ons/neural</code>; and kernel drivers that publish the processors under <code>/dev/npu</code>.</p>'
    body += pre('''#include <NeuralKit.h>

BNeuralModel model("/boot/home/models/mobilenet_v1_1.0_224_quant.tflite");
BNeuralSession session(model);              // loads it onto the best device
if (session.InitCheck() != B_OK)
	return session.InitCheck();

BNeuralUtils::SetTensorFromBitmap(session.InputAt(0), bitmap);
if (session.Run() == B_OK)
	int64 best = session.OutputAt(0)->IndexOfMaximum();''')
    body += '<p>Link with <code>-lneural -lbe</code>. The kit ships in air/OS releases from 9 November 2026 on (the first was the ARM64 release hrev60207+2552), together with the <code>neural</code> command and the Lookout demo.</p>'
    body += '<div class="doc-cards three">'
    body += f'<a class="doc-card" href="{s.url("docs/neural/examples/")}"><strong>Examples</strong><span>Seven complete programs, run on a ROCK 5 ITX, with their output.</span></a>'
    body += f'<a class="doc-card" href="{s.url("docs/neural/reference/")}"><strong>Reference</strong><span>Every class, function, constant and message of the kit.</span></a>'
    body += f'<a class="doc-card" href="#backends"><strong>Writing a back end</strong><span>Make new hardware available to every program that uses the kit.</span></a>'
    body += '</div></section>'

    body += '<section id="devices"><h2>What runs where</h2>'
    body += table(['Machine', 'Device', 'Back end', 'Runs'], [
        ['Every machine', '<code>cpu</code>', 'built into the kit', 'every operator the kit knows, float and quantized; the reference the others are checked against'],
        ['ROCK 5 ITX and other RK3588 boards', '<code>rk3588_npu/0</code>', '<code>rk3588_npu.neural</code>, driver <code>/dev/npu/rk3588/0</code>', '8-bit quantized convolutions; the rest of the network on the CPU'],
        ['Machines with a Vulkan driver (NVK on NVIDIA, RADV on AMD)', '<code>vulkan/0</code>', '<code>vulkan.neural</code>, the graphics driver', 'float32 networks, in compute shaders'],
        ['Framework 13 with Ryzen AI 300 (AMD XDNA NPUs)', '<code>amdxdna/0</code>', '<code>amdxdna.neural</code>, driver <code>/dev/npu/amdxdna/0</code>', 'compiled NPU designs (“design bundles”) for parts of a network'],
    ])
    body += f'<p>See <a href="#status">Hardware status</a> for what was measured on each.</p></section>'

    body += '<section id="architecture"><h2>How it fits together</h2>'
    body += '''<div class="stack" role="img" aria-label="Layers of the Neural Kit: the application uses models, sessions and tensors in libneural.so, which splits the network between its CPU interpreter and back-end add-ons, which talk to kernel drivers.">
<div class="layer app"><span class="layer-name">Application</span><div class="chips"><span>BNeuralModel</span><span>BNeuralSession</span><span>BTensor</span><span>BSpeechRecognizer</span></div></div>
<div class="layer kit"><span class="layer-name">libneural.so</span><div class="chips"><span>TensorFlow Lite loader</span><span>partitioner</span><span>CPU interpreter (“cpu”)</span><span>BNeuralRoster</span></div></div>
<div class="layer addon"><span class="layer-name">add-ons/neural</span><div class="chips"><span>rk3588_npu.neural</span><span>vulkan.neural</span><span>amdxdna.neural</span><span>your back end</span></div></div>
<div class="layer kernel"><span class="layer-name">Kernel</span><div class="chips"><span>/dev/npu/rk3588/0</span><span>graphics driver</span><span>/dev/npu/amdxdna/0</span></div></div>
</div>'''
    body += '<ul class="checks">'
    body += f'<li><strong>A model</strong> ({ref("BNeuralModel")}) is a network read into the kit’s own form: tensors, operators and weights. The file is mapped, not read, so weights are paged in on demand and shared between teams. Models cannot be changed, and copies share the network.</li>'
    body += f'<li><strong>A session</strong> ({ref("BNeuralSession")}) is a model made ready on one device. The kit asks the device’s back end which operators it can run, cuts the network into stretches of those and stretches of the rest, has the back end make a program for each of its stretches, and prepares the CPU interpreter for everything else. A run the device fails is done by the CPU, and a device that goes away, or fails three runs in a row, loses its stretches to the CPU for good. A session always works and gives the same answers: bit for bit for quantized networks on the CPU, and within measured tolerances on devices.</li>'
    body += f'<li><strong>The roster</strong> ({ref("BNeuralRoster")}) knows the devices. It loads the back ends the first time it is asked something. A back end whose hardware is not there reports no devices and costs nothing more.</li>'
    body += '<li><strong>Back ends</strong> are add-ons, found like translators: in <code>add-ons/neural</code> of the user’s non-packaged directory, the user’s packages, the system’s non-packaged directory and the system package, in that order. The first file of a name wins, so a back end under development shadows the packaged one.</li>'
    body += '<li><strong>Kernel drivers</strong> only give access to a processor: memory it can reach, power, a queue of jobs. They know nothing of networks. Listing <code>/dev/npu</code> loads them, so a machine that never runs a network never loads them.</li>'
    body += '</ul></section>'

    body += '<section id="tensors"><h2>Tensors</h2>'
    body += f'<p>A {ref("BTensorInfo")} describes a tensor: element type (<code>B_NEURAL_FLOAT32</code>, <code>B_NEURAL_UINT8</code>, <code>B_NEURAL_INT8</code> and others), shape (up to eight dimensions; pictures are batch, height, width, channels) and, for quantized tensors, the scale and zero point that map stored integers to real values: <code>real = scale × (stored − zero point)</code>.</p>'
    body += f'<p>A {ref("BTensor")} is a description plus the numbers. It owns its memory or uses the caller’s. <code>Data()</code> is the raw storage; <code>ValueAt()</code>, <code>GetValues()</code>, <code>SetValueAt()</code> and <code>SetValues()</code> read and write real values whatever the storage, so the same code handles a float model and its quantized sibling. A tensor is a <code>BArchivable</code>: archived into a <code>BMessage</code> with its numbers, it can be sent to another team or kept in a file or attribute.</p></section>'

    body += '<section id="models"><h2>Models</h2>'
    body += pre('''BNeuralModel model;
status_t status = model.SetTo(&ref);        // or a path, a BDataIO, a buffer
if (status != B_OK)
	fprintf(stderr, "%s: %s\\n", neural_error_string(status), model.ErrorDetails());

for (int32 i = 0; i < model.CountInputs(); i++) {
	BTensorInfo info;
	model.GetInputInfo(i, &info);
	puts(info.ToString());     // input uint8 [1, 224, 224, 3] scale 0.0078125 zero 128
}''')
    body += '<p>The kit reads TensorFlow Lite files (<code>.tflite</code>, schema version 3) itself, with a reader that checks every offset, since a model file may come from anywhere. <code>BNeuralModel::IsModel()</code> tells whether a file is a model without reading all of it, and <code>GetInfo()</code> returns the name, description, format, kinds of operator and bytes of weights.</p>'
    body += '<p>Shapes are fixed when a model is made: there are no dynamic shapes and no control flow. A model keeps nothing between runs: one that works in steps, like the decoder of a speech model, gets what its earlier steps computed as inputs. A model with an operator the kit does not know fails to load with <code>B_NEURAL_UNSUPPORTED_OPERATOR</code>, and <code>ErrorDetails()</code> names the operator.</p>'
    body += f'<p>{ref("BNeuralModelBuilder")} makes a model in memory, operator by operator, for programs that compute their network and for tests. See {ex("builder", "the builder example")}.</p></section>'

    body += '<section id="choosing"><h2>Devices and choosing one</h2>'
    body += f'<p>A {ref("BNeuralDevice")} names a device. Its <code>ID()</code> (<code>"cpu"</code>, <code>"rk3588_npu/0"</code>, <code>"vulkan/0"</code>) is stable across restarts: keep it in your settings. <code>CountSupportedOperators(model)</code> says how much of a model a device would run without loading anything.</p>'
    body += f'<p>When a program does not choose, <code>BNeuralRoster::GetDefaultDevice()</code> does: an NPU, else a graphics processor, else the CPU, among the devices that run at least part of the model. Flags change the choice:</p>'
    body += table(['Flag', 'Effect'], [
        ['<code>B_NEURAL_PREFER_SPEED</code> (0)', 'the fastest kind of device: NPU, GPU, CPU (the default)'],
        ['<code>B_NEURAL_PREFER_LOW_POWER</code>', 'NPU, else CPU, else GPU'],
        ['<code>B_NEURAL_NO_FALLBACK</code>', 'only devices that run the whole model; a session fails with <code>B_NEURAL_NOT_ACCELERATED</code> rather than use the CPU for part of it'],
        ['<code>B_NEURAL_CPU_ONLY</code>', 'the CPU, whatever else there is'],
        ['<code>B_NEURAL_PROFILE</code>', 'sessions keep per-operator times'],
    ])
    body += '<p>The user’s choice comes first when it can do the job. It is set in <code>~/config/settings/neural</code> (driver settings syntax) or in the environment:</p>'
    body += pre('''preferred_device rk3588_npu/0      # or NEURAL_DEVICE=rk3588_npu/0
disable_backend vulkan             # or NEURAL_DISABLE_BACKENDS="vulkan" ("all": the CPU only)''')
    body += '<p><code>NEURAL_THREADS=n</code> sets how many threads the CPU device uses (default: one per CPU, at most 16).</p>'
    body += f'<p><code>BNeuralRoster::StartWatching()</code> sends <code>B_NEURAL_DEVICE_ADDED</code> and <code>B_NEURAL_DEVICE_REMOVED</code> as devices come and go. A session whose device went away keeps working on the CPU; set it up again to move it back. See {ex("devices", "the devices example")}.</p></section>'

    body += '<section id="sessions"><h2>Sessions and runs</h2>'
    body += pre('''BNeuralSession session;
status_t status = session.SetTo(model);            // the default device
// or: session.SetTo(model, device, B_NEURAL_NO_FALLBACK);

BTensor* input = session.InputAt(0);               // owned by the session
// fill input->Data(), or use BNeuralUtils
status = session.Run();                            // returns when done
const BTensor* output = session.OutputAt(0);''')
    body += '<p>Setting a session up is the slow part; running is fast and can be repeated as often as needed. Inputs and outputs belong to the session and keep their memory between runs. A session runs one thing at a time (<code>B_BUSY</code> otherwise); several sessions, including sessions of the same model, run at once and share a device.</p>'
    body += '<p>A window must not block on a network. <code>RunAsync()</code> returns at once and sends a message when the run is over:</p>'
    body += pre('''session.RunAsync(BMessenger(this));              // B_NEURAL_RUN_COMPLETED when done

void MyWindow::MessageReceived(BMessage* message)
{
	if (message->what == B_NEURAL_RUN_COMPLETED
		&& message->GetInt32("neural:status", B_ERROR) == B_OK) {
		// session.OutputAt() is ready; "neural:duration" says how long it took
	}
}''')
    body += f'<p>A message of your own can replace <code>B_NEURAL_RUN_COMPLETED</code>; the <code>neural:</code> fields are added to it, including a token and a pointer to the session. Leave the inputs alone and do not read the outputs until the message arrives. Deleting a session waits for its run to end: a run cannot be cancelled yet. <code>GetRunInfo()</code> tells how the model was split and how long runs take; <code>GetOperatorInfo()</code> tells where each operator runs and, with <code>B_NEURAL_PROFILE</code>, how long it took. See {ex("async", "the asynchronous example")}.</p></section>'

    body += '<section id="pictures"><h2>Pictures, labels and results</h2>'
    body += f'<p>{ref("BNeuralUtils")} ties tensors to the Interface Kit. <code>SetTensorFromBitmap()</code> scales a bitmap of any size and of the usual colour spaces into an image tensor (uint8, int8 or float; one or three channels), stretched, cropped or letterboxed, and records a {ref("neural_image_mapping")} to map results back. <code>GetLabels()</code> reads the label files models come with, <code>GetTopValues()</code> picks a classifier’s best classes, and <code>IsDetector()</code> and <code>GetDetections()</code> read what a detection model found:</p>'
    body += pre('''neural_image_mapping mapping;
BNeuralUtils::SetTensorFromBitmap(session.InputAt(0), bitmap, NULL, NULL, &mapping);
session.Run();

neural_detection found[32];
int32 count = BNeuralUtils::GetDetections(session, found, 32);
for (int32 i = 0; i < count; i++) {
	BRect box = mapping.ToBitmap(found[i].left, found[i].top,
		found[i].right, found[i].bottom);
	// labels.StringAt(found[i].class_index + 1), found[i].score
}''')
    body += f'<p>See {ex("classify", "classifying")} and {ex("detect", "detecting")} pictures.</p></section>'

    body += '<section id="speech"><h2>Speech recognition</h2>'
    body += f'<p>{ref("BSpeechRecognizer")} turns speech into text on the machine itself, with a Whisper model the kit runs. Nothing leaves the machine. Audio goes in as it is recorded, in any raw format of the Media Kit; text comes out as messages, and nothing the caller does waits for the model.</p>'
    body += pre('''BSpeechRecognizer recognizer;
status_t status = recognizer.SetTo();           // the first model installed
recognizer.SetTarget(BMessenger(this));
recognizer.SetInterimInterval(2000000);         // also read unfinished audio

recognizer.Start(&format);                      // a media_raw_audio_format
// for every buffer the recording gives, from whatever thread has it:
recognizer.Feed(buffer, size);
// when the recording is over:
recognizer.Finish();

void MyWindow::MessageReceived(BMessage* message)
{
	switch (message->what) {
		case B_SPEECH_RESULT:
		{
			const char* text = message->GetString("speech:text", "");
			if (message->GetBool("speech:final", false))
				fTranscript << text << " ";     // a phrase that stands
			else
				fPending = text;                // replaces the one before
			break;
		}
		case B_SPEECH_FINISHED:
			// "speech:status": the recording is done with
			break;
	}
}''')
    body += '<p>For a complete recording, <code>Transcribe()</code> returns the text directly, and <code>CountSegments()</code> and <code>GetSegment()</code> give each phrase with its start and end time.</p>'
    body += '<p><strong>How it works.</strong> Whisper takes 30 seconds of audio at a time. The recognizer’s thread makes a log-mel spectrogram of each window, runs the encoder once, and runs the decoder once per token, choosing the likeliest token each time. The model writes timestamps between phrases: a phrase is <em>final</em> once the model has seen its end, and the next window starts where the last whole phrase ended. A recording shorter than a window therefore gives its final phrases only at <code>Finish()</code>; with <code>SetInterimInterval()</code> you also get non-final readings while it is spoken. Audio of any rate, sample format and up to eight channels is brought to 16 kHz mono as it is fed.</p>'
    body += '<p><strong>Models.</strong> A speech model is a directory with a <code>speech.conf</code>, the encoder and decoder networks, the vocabulary and the mel filters, under <code>neural/models</code> of a data directory (for example <code>~/config/non-packaged/data/neural/models/whisper-tiny.en</code>). No model ships in the images yet. <code>tools/airos/neural/fetch-models.sh &lt;directory&gt; speech</code> in the haiku repository downloads OpenAI’s Whisper tiny.en checkpoint by checksum and converts it on a Linux host (Python with numpy, flatbuffers and ai-edge-litert); <code>speech-multilingual</code> fetches Whisper tiny, which knows 99 languages.</p>'
    body += '<p><strong>Limits.</strong> Decoding is greedy, with no beam search and no second tries, so a hard stretch of audio can give repeated or wrong text. Nothing detects the end of speech: the caller says when a recording is over. All of the work runs on the CPU. Each recording costs about 425 MB of memory while it is recognized, the 150 MB of mapped model files included. On a ROCK 5 ITX a 30-second window full of speech takes 2.2 to 2.3 s, and 11 seconds of speech take 1.5 to 1.6 s.</p>'
    body += f'<p>Summit’s <code>webkitSpeechRecognition</code> is built on this class. See {ex("transcribe", "the transcription example")} and {ex("summit", "Summit’s speech recognition")}.</p></section>'

    body += '<section id="operators"><h2>Operators</h2>'
    body += '<p>The kit’s operators follow TensorFlow Lite’s, whose quantized arithmetic is specified to the bit. The CPU kernels reproduce it, which makes the CPU device the reference every back end is checked against.</p>'
    body += table(['Group', 'Operators'], [
        ['Convolution', '<code>CONV_2D</code>, <code>DEPTHWISE_CONV_2D</code>, <code>TRANSPOSE_CONV</code>, <code>FULLY_CONNECTED</code>'],
        ['Pooling', '<code>AVERAGE_POOL_2D</code>, <code>MAX_POOL_2D</code>, <code>MEAN</code>'],
        ['Arithmetic', '<code>ADD</code>, <code>SUB</code>, <code>MUL</code>, <code>DIV</code>, <code>MAXIMUM</code>, <code>MINIMUM</code> (broadcasting)'],
        ['Activation', '<code>RELU</code>, <code>RELU6</code>, <code>LEAKY_RELU</code>, <code>PRELU</code>, <code>LOGISTIC</code>, <code>TANH</code>, <code>HARD_SWISH</code>, <code>SOFTMAX</code>'],
        ['Shape', '<code>RESHAPE</code>, <code>SQUEEZE</code>, <code>CONCATENATION</code>, <code>PAD</code>, <code>TRANSPOSE</code>, <code>STRIDED_SLICE</code>, <code>RESIZE_BILINEAR</code>, <code>RESIZE_NEAREST</code>'],
        ['Types', '<code>QUANTIZE</code>, <code>DEQUANTIZE</code>'],
        ['Transformers', '<code>BATCH_MATMUL</code>, <code>GELU</code>, <code>GATHER</code>, <code>SQUARED_DIFFERENCE</code>, <code>RSQRT</code> (float32)'],
        ['Detection', '<code>DETECTION_POSTPROCESS</code> (boxes, classes, scores and count from a single-shot detector)'],
    ])
    body += f'<p>That covers the MobileNet family (V1 and V2, classification and SSD detection), EfficientNet-Lite, DeepLab V3, BlazeFace and the encoder and decoder of Whisper. Weights stored as 8-bit integers with floating-point activations (“dynamic range” quantization) are not supported yet. Parameters are in the {s.link(s.url("docs/neural/reference/#operators"), "reference")}.</p></section>'

    body += '<section id="errors"><h2>Errors</h2>'
    body += '<p>Besides the usual ones (<code>B_NO_INIT</code>, <code>B_BAD_VALUE</code>, <code>B_NO_MEMORY</code>, <code>B_BUSY</code>, file errors), the kit has its own. <code>neural_error_string()</code> describes any of them.</p>'
    body += table(['Error', 'When'], [
        ['<code>B_NEURAL_BAD_MODEL</code>', 'the file is not a model, or is damaged'],
        ['<code>B_NEURAL_UNKNOWN_FORMAT</code>', 'no loader knows the format or version'],
        ['<code>B_NEURAL_UNSUPPORTED_OPERATOR</code>', 'the model has an operator the kit has no kernel for'],
        ['<code>B_NEURAL_TYPE_MISMATCH</code>, <code>B_NEURAL_SHAPE_MISMATCH</code>', 'a tensor does not fit'],
        ['<code>B_NEURAL_NO_DEVICE</code>', 'no such device'],
        ['<code>B_NEURAL_DEVICE_LOST</code>', 'the device went away and the CPU could not take over (<code>B_NEURAL_NO_FALLBACK</code>)'],
        ['<code>B_NEURAL_NOT_ACCELERATED</code>', '<code>B_NEURAL_NO_FALLBACK</code> was given and the device cannot run the whole model'],
    ])
    body += '</section>'

    body += '<section id="command"><h2>The neural command</h2>'
    body += pre('''neural devices                        the devices, and what their back ends say about them
neural info model.tflite              inputs, outputs, operators, and what each device runs of it
neural run model.tflite -i cat.png -l labels.txt
                                      the best classes or the detections for a picture;
                                      -d <device>, --cpu, --no-fallback, -n <runs>,
                                      -p (where each operator ran and how long), -o <file>
neural compare model.tflite -d rk3588_npu/0
                                      a device against the CPU on the same input;
                                      --tolerance <steps>, --float-tolerance <fraction>
neural bench model.tflite             times the model on every device
neural transcribe speech.wav          what is said in a recording, phrase by phrase;
                                      --model <name or directory>, -d <device>, --cpu,
                                      --language <code>, --no-timestamps, --interim <seconds>''')
    body += '<p>Without <code>-i</code>, the input is noise that is the same on every run.</p></section>'

    body += '<section id="backends"><h2>Writing a back end</h2>'
    body += f'<p>A back end makes a kind of hardware available to every program that uses the kit. It is one class in an add-on named <code>&lt;name&gt;.neural</code>, implementing {ref("BNeuralBackend")}:</p>'
    body += '<ul class="checks">'
    body += '<li><code>CountDevices()</code> looks for hardware, usually by opening the driver’s nodes under <code>/dev/npu</code>; <code>GetDeviceInfo()</code> describes each device.</li>'
    body += f'<li><code>GetSupportedOperators()</code> must be exact and quick: it sees the network as a {ref("BNeuralGraph")} (types, shapes, quantization, parameters) and says yes only to what the device computes correctly. The kit asks it before anything is loaded, and also just to choose a device.</li>'
    body += '<li><code>CreateProgram()</code> gets a partition: operators that follow one another, the tensors they need from outside and the tensors they make that are needed outside. It converts and uploads the weights and returns a <code>BNeuralProgram</code>. An error means “run this stretch on the CPU”.</li>'
    body += '<li><code>BNeuralProgram::Run()</code> gets the memory of the partition’s inputs and outputs in the graph’s types and NHWC layout, computes, and returns when the outputs are written. On an error the kit computes the stretch on the CPU for that run and tries the device again next time; three failures in a row, or <code>B_NEURAL_DEVICE_LOST</code>, hand the stretch to the CPU for good.</li>'
    body += '<li>Programs of different sessions run at the same time, so a back end must be thread safe.</li>'
    body += '</ul>'
    body += f'<p>Check a back end with <code>neural compare &lt;model&gt; -d &lt;device&gt;</code>, which runs the device and the CPU on the same input and shows the differences, and with single-operator models made by <code>BNeuralModelBuilder</code>. {ex("backend", "The example back end")} is a complete add-on to start from.</p>'
    body += '<p>Kernel drivers live in <code>add-ons/kernel/drivers/npu</code> and publish <code>/dev/npu/&lt;driver&gt;/&lt;n&gt;</code>. They give access to memory the processor can reach, power and a job queue, and should touch no hardware until the device is opened. The RK3588 driver also isolates clients: each open has its own IOMMU address space, and a job that reaches outside its buffers fails with <code>B_BAD_ADDRESS</code>.</p></section>'

    body += '<section id="status"><h2>Hardware status</h2>'
    body += '<p>Measured on 9 and 10 November 2026. “Agrees” means <code>neural compare</code> against the CPU device on the same input.</p>'
    body += table(['Device', 'Model', 'On the device', 'Against the CPU', 'CPU', 'Device'], [
        ['RK3588 NPU (ROCK 5 ITX)', 'MobileNet V1 quantized', '28 of 31 operators', 'equal', '21.8 ms', '8.5 ms'],
        ['', 'MobileNet V2 quantized', '63 of 65', 'within 3 quantized steps; same top five', '19.0 ms', '10.0 ms'],
        ['', 'SSD MobileNet V1 quantized', '47 of 64', 'same detections; scores within 0.008', '34.3 ms', '14.7 ms'],
        ['Vulkan, GTX 1070 (NVK)', 'MobileNet V2 float', '66 of 66', 'relative difference 2e-6', '29.5 ms', '3.9 ms'],
        ['Vulkan, Radeon 840M (RADV)', 'MobileNet V2 float', '66 of 66', 'relative difference 2e-6', '15.1 ms', '8.9 ms'],
        ['AMD XDNA NPU (Ryzen AI 5 340)', '1×1 int8 convolution (one design bundle)', 'all', 'equal in all 65536 outputs', '0.35 ms', '0.11 ms'],
    ])
    body += '<ul class="checks">'
    body += '<li><strong>CPU.</strong> 726 generated single-operator models and 9 real models agree with TensorFlow Lite’s reference kernels on every tensor (integers equal, floats within 1e-4). 3737 deliberately damaged model files are refused or run without a crash, also under the address and undefined-behaviour sanitizers. x86-64 uses SSE2 only so far.</li>'
    body += '<li><strong>RK3588 NPU.</strong> Quantized <code>CONV_2D</code> and <code>DEPTHWISE_CONV_2D</code> (uint8 or int8, kernels up to 7, strides 1 and 2), with a fused <code>ADD</code>; one of the three cores, at 198 MHz.</li>'
    body += '<li><strong>Vulkan.</strong> float32 only: convolutions, fully connected, pooling, arithmetic, activations, softmax, reshapes, concatenation, <code>MEAN</code>, <code>PAD</code>, <code>RESIZE_BILINEAR</code>. Not yet tried on Turnip, V3DV or PowerVR.</li>'
    body += '<li><strong>AMD XDNA.</strong> The NPU runs designs compiled on a Linux host with mlir-aie and Peano, found as design bundles by a key computed from a stretch of a network. Only one bundle exists. There is no AMD IOMMU driver, so the device can only be opened by root; for everyone else the CPU runs the model.</li>'
    body += '<li><strong>Speech.</strong> CPU only; the same text and times as Whisper’s reference on three test recordings, on ARM64 and x86-64.</li>'
    body += '</ul>'
    body += f'<p>The full measurements, test methods and open points are in {s.source("docs/airos/NEURAL-KIT.md", "the Neural Kit design notes ↗")}.</p></section>'

    body += '<section id="limits"><h2>Not yet</h2><ul class="checks">'
    body += '<li>Model formats other than TensorFlow Lite (ONNX would be a second loader).</li>'
    body += '<li>Cancelling a run, and sharing device memory between sessions and the program’s tensors (tensors are copied across).</li>'
    body += '<li>Speech on a GPU or NPU, voice activity detection, quantized speech models, and recognition as a media node.</li>'
    body += '<li>The RK3588’s other two NPU cores; designs for real networks on AMD XDNA.</li>'
    body += '<li>The Dragon Q8B’s Hexagon NPU, which has no open compiler or runtime (its Adreno GPU would work through the Vulkan back end, untried).</li>'
    body += '<li>Models in the system images: fetch them with <code>fetch-models.sh</code> for now.</li>'
    body += '</ul></section>'

    toc = [('overview', 'Overview'), ('devices', 'What runs where'), ('architecture', 'How it fits together'), ('tensors', 'Tensors'),
           ('models', 'Models'), ('choosing', 'Devices'), ('sessions', 'Sessions and runs'), ('pictures', 'Pictures and results'),
           ('speech', 'Speech recognition'), ('operators', 'Operators'), ('errors', 'Errors'), ('command', 'The neural command'),
           ('backends', 'Writing a back end'), ('status', 'Hardware status'), ('limits', 'Not yet')]
    doc_page(s, 'docs/neural/', 'Neural Kit', 'The air/OS Neural Kit: neural-network inference on NPUs, graphics processors and the CPU through one API, and on-device speech recognition.',
             'Documentation · Neural Kit', 'Neural networks, on every processor.',
             'The Neural Kit runs models on NPUs, graphics processors and the CPU through one API, splitting each network between the device and the CPU so it always gives the same answers. It also turns speech into text on the machine itself.', toc, body)


# ---------------------------------------------------------------- Neural Kit reference

def neural_reference(s):
    body = f'<aside class="note">The kit’s headers are in <code>/boot/system/develop/headers/os/neural/</code>; <code>#include &lt;NeuralKit.h&gt;</code> includes them all. Link with <code>-lneural</code>. For concepts and a tour, read the {s.link(s.url("docs/neural/"), "Neural Kit guide")}.</aside>'
    toc = []
    seen = set()
    for header in s.api['headers']:
        toc.append((header['id'], e(header['title'])))
        body += f'<section class="api-header" id="{header["id"]}"><div class="kit-head"><h2>{e(header["title"])}</h2><span>{e(header["header"])}</span></div>'
        body += f'<p class="section-lead">{s.inline(header["text"])}</p>'
        body += s.source('headers/os/' + header['header'], 'Header source ↗')
        for item in header['items']:
            anchor = item['name'] if re.fullmatch(r'[A-Za-z_]\w*', item['name']) else header['id'] + '-' + slug(item['name'])
            assert anchor not in seen, anchor
            seen.add(anchor)
            title = f'<code>{e(item["name"])}</code>' if anchor == item['name'] else e(item['name'])
            base = f' <span class="api-base">: public {e(item["base"])}</span>' if item.get('base') else ''
            body += f'<article class="api-item" id="{anchor}"><div class="api-change-head"><span class="kind kind-ref">{e(item["kind"])}</span><h3>{title}{base}</h3></div>'
            if item.get('text'):
                body += f'<p>{s.inline(item["text"])}</p>'
            if item.get('sig'):
                body += pre(item['sig'], 'sig')
            if item.get('members'):
                body += '<dl class="api-members">' + ''.join(f'<dt>{pre(m["sig"], "sig")}</dt><dd>{s.inline(m["text"])}</dd>' for m in item['members']) + '</dl>'
            if item.get('values'):
                body += table(['Name', 'Meaning'], [[f'<code>{e(n)}</code>', s.inline(t)] for n, t in item['values']])
            body += '</article>'
        body += '</section>'
    doc_page(s, 'docs/neural/reference/', 'Neural Kit reference', 'Reference for the air/OS Neural Kit: BNeuralModel, BNeuralSession, BNeuralRoster, BTensor, BNeuralUtils, BSpeechRecognizer, operators and the back-end API.',
             'Documentation · Neural Kit reference', 'Neural Kit reference.',
             'Every class, function, constant and message of the kit, header by header, from <code>NeuralDefs.h</code> to the back-end API.', toc, body)


# ---------------------------------------------------------------- Neural Kit examples

EXAMPLES = [
    ('classify', 'Classify a picture', 'classify.cpp', 'The smallest useful program: load a model, set up a session on the best device, put a picture into the input tensor, run it, and print the five best classes with their labels. On the ROCK 5 the kit puts 28 of the 31 operators on the NPU by itself.'),
    ('detect', 'Find objects in a picture', 'detect.cpp', 'A detection model returns boxes as fractions of its input. The <code>neural_image_mapping</code> filled in by <code>SetTensorFromBitmap()</code> takes them back to the picture’s pixels. Detection label files begin with a line for “nothing”, so the label of class <i>n</i> is at <i>n</i> + 1.'),
    ('devices', 'List devices and choose one', 'devices.cpp', 'What the roster knows: each device, how much of a model it would run (asked without loading anything), what its back end reports, and which device the kit would choose under each preference. A float model would show the NPU running none of it, and the kit choosing the CPU.'),
    ('async', 'Run without blocking', 'async.cpp', 'The pattern Lookout uses to keep up with a camera. A looper owns the session and starts runs with <code>RunAsync()</code>; frames that arrive during a run replace each other, and the newest is taken when the run is over. Three frames went in while the first was being processed, so the second was dropped: two results.'),
    ('builder', 'Build a network in code', 'builder.cpp', 'A network made with <code>BNeuralModelBuilder</code>, run on the CPU as the reference and on the device the kit chooses, then compared. This is also how a back end is tested, one operator at a time. Binary operators take <code>neural_binary_params</code>, and an activation can be fused into them. On the ROCK 5 the kit chose the CPU, because the NPU runs only quantized networks.'),
    ('transcribe', 'Transcribe a recording', 'transcribe.cpp', 'Speech to text, fed as a live recording would be: a file decoded by the Media Kit, handed to <code>BSpeechRecognizer</code> buffer by buffer in whatever format the decoder gives, with the phrases arriving as messages to a looper. Feeding from a microphone works the same way, from the thread that records.'),
    ('backend', 'A back end for new hardware', 'backend.cpp', 'A complete back-end add-on. It claims float32 <code>RELU</code> operators and runs stretches of them in its own program, standing in for a device. Swap the body of <code>Run()</code> for a job submitted to your driver and the rest of the kit (loading, partitioning, CPU fallback, comparison) comes for free. Installed in <code>~/config/non-packaged/add-ons/neural</code>, it appeared in <code>neural devices</code> and ran its two operators of a test network correctly.'),
]


def neural_examples(s):
    folder = s.root / 'content/docs/examples'
    body = '<section id="setup"><h2>Before you start</h2>'
    body += '<p>Each example is a complete program. They were compiled against air/OS’s headers and libraries and run on a ROCK 5 ITX (RK3588, air/OS ARM64 release hrev60207+2552) on 10 November 2026; the output shown is what they printed there. That board’s image has no JPEG translator, so the pictures are PNG.</p>'
    body += '<p>The public test models come from TensorFlow’s model zoo. The script in the haiku repository downloads them by checksum into a data directory, where Lookout also finds them:</p>'
    body += pre('''# in a checkout of airos-works/haiku
# MobileNet V1 and V2, SSD MobileNet V1 and their labels:
tools/airos/neural/fetch-models.sh ~/config/non-packaged/data
# Whisper tiny.en, converted on a Linux host:
tools/airos/neural/fetch-models.sh ~/config/non-packaged/data speech''')
    body += f'<p>{s.source("tools/airos/neural/fetch-models.sh", "fetch-models.sh ↗")} lists the files, their sources and licences.</p></section>'
    toc = [('setup', 'Before you start')]
    for anchor, title, file, text in EXAMPLES:
        toc.append((anchor, e(title)))
        code = (folder / file).read_text()
        out = folder / (file.rsplit('.', 1)[0] + '.out')
        body += f'<section class="example" id="{anchor}"><div class="kit-head"><h2>{e(title)}</h2><span>{e(file)}</span></div><p>{text}</p>'
        body += pre(code, 'example-code')
        if out.exists():
            body += '<p class="output-label">Output on the ROCK 5 ITX</p>' + pre(out.read_text(), 'output')
        body += '</section>'

    toc.append(('summit', 'Speech in a web page'))
    body += '<section class="example" id="summit"><div class="kit-head"><h2>Speech in a web page</h2><span>Summit</span></div>'
    body += '<p>Summit’s <code>webkitSpeechRecognition</code> is a <code>BSpeechRecognizer</code> fed from the microphone. A page uses the standard Web Speech API; nothing leaves the machine. The interface exists only where the system has the recognizer, so <code>\'webkitSpeechRecognition\' in window</code> is false on stock Haiku.</p>'
    body += pre('''const recognition = new webkitSpeechRecognition();
recognition.lang = 'en-US';
recognition.interimResults = true;      // SetInterimInterval()
recognition.onresult = event => {
	const result = event.results[event.results.length - 1];
	console.log(result[0].transcript, result.isFinal);   // "speech:final"
};
recognition.start();                    // Start(), then Feed() from the microphone''')
    body += f'<p>The first <code>start()</code> asks for the microphone. With a model installed, it was checked on a Framework 13 with a Logitech C920’s microphone. Summit’s {s.link(GITHUB_SUMMIT_DOC, "speech recognition notes ↗")} cover events, errors and what the machine needs.</p></section>'

    toc.append(('lookout', 'Lookout'))
    body += '<section class="example" id="lookout"><div class="kit-head"><h2>Lookout: the kit in an application</h2><span>Demos menu</span></div>'
    body += '<p>Lookout, in the Demos menu, shows what a detection or classification model finds in a picture or in a camera’s video, on the device of your choice. It is the kit used the way an application should use it:</p><ul class="checks">'
    body += '<li>An engine looper owns the model and the session, so setting a session up (seconds on a GPU) never holds up the window.</li>'
    body += '<li>Runs use <code>RunAsync()</code> with the engine as target; camera frames replace each other in a slot while a run is going on.</li>'
    body += '<li>It watches the roster: when a device is added or removed, the session is set up again, and the user’s choice is kept by device ID.</li>'
    body += '<li>After each run, <code>GetRunInfo()</code> shows how many operators ran on the device and on the CPU, and whether the device failed runs.</li>'
    body += '<li>Pictures are fitted with <code>SetTensorFromBitmap()</code>, and detection boxes taken back with the mapping.</li></ul>'
    body += f'<p>On a Framework 13 it ran SSD MobileNet V1 on the CPU at the camera’s 30 frames per second, 13 to 15 ms a run, and MobileNet V2 on the Radeon GPU through Vulkan at 15 to 17 ms. {s.source("src/apps/lookout/Engine.cpp", "Engine.cpp ↗")} is the place to start reading; {s.source("src/apps/lookout", "the whole app ↗")}.</p></section>'

    toc.append(('more', 'More code'))
    body += '<section class="example" id="more"><div class="kit-head"><h2>More code to read</h2></div><ul class="checks">'
    body += f'<li>{s.source("src/bin/neural/neural.cpp", "src/bin/neural/neural.cpp ↗")}: the <code>neural</code> command: info, run, compare, bench and transcribe.</li>'
    body += f'<li>{s.source("src/tests/kits/neural/neural_kit_test.cpp", "neural_kit_test.cpp ↗")}: the kit’s classes, with a back end inside the test; run in every image build’s smoke test.</li>'
    body += f'<li>{s.source("src/tests/kits/neural/speech_test.cpp", "speech_test.cpp ↗")}: the speech front end, model directories, and <code>BSpeechRecognizer</code> messages, interim results, <code>Cancel()</code> and deletion mid-work.</li>'
    body += f'<li>{s.source("src/tests/kits/neural/vulkan_backend_test.cpp", "vulkan_backend_test.cpp ↗")} and {s.source("src/tests/kits/neural/rk3588_npu_backend_test.cpp", "rk3588_npu_backend_test.cpp ↗")}: single operators on a device against the CPU.</li>'
    body += f'<li>{s.source("src/add-ons/neural", "src/add-ons/neural ↗")}: the three real back ends.</li>'
    body += '</ul></section>'

    doc_page(s, 'docs/neural/examples/', 'Neural Kit examples', 'Complete Neural Kit example programs for air/OS: classification, detection, devices, asynchronous runs, building networks, speech transcription and a back end, with output from a ROCK 5 ITX NPU.',
             'Documentation · Neural Kit examples', 'Neural Kit examples.',
             'Complete programs, each compiled against air/OS and run on a ROCK 5 ITX with its NPU, with the output they printed. Copy one and change it.', toc, body)


GITHUB_SUMMIT_DOC = ''


def build(page, url, link, intro, root, github):
    global GITHUB_SUMMIT_DOC
    GITHUB_SUMMIT_DOC = github + '/summit/blob/main/docs/speech-recognition.md'
    s = Site(page, url, link, intro, root, github)
    overview(s)
    kit_differences(s)
    neural_guide(s)
    neural_reference(s)
    neural_examples(s)
