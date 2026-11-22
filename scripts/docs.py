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


def doc_page(s, path, title, description, kicker, heading, lead, toc, body, tabs=True):
    # The API pages share a row of tabs; guides such as Virtualization have none.
    links = ''.join(s.link(s.url(p), label, 'active' if p == path else '') for p, label in SECTIONS)
    nav = f'<nav class="doc-tabs" aria-label="Documentation">{links}</nav>' if tabs else ''
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
    body += '</div>'
    body += f'<p>To install air/OS on a PC, an ARM64 board, a Raspberry Pi, a Cubie A7S or an Intel Mac, see the {s.link(s.url("docs/install/"), "installation guides →")} To try your app, or air/OS itself, without a spare computer, run it in a virtual machine: {s.link(s.url("docs/virtualization/"), "QEMU and UTM set-up →")}</p></section>'

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


# ---------------------------------------------------------------- virtualization

def virtualization(s):
    """Running air/OS in a virtual machine: QEMU on Linux, UTM on a Mac.

    Checked on 17 November 2026 with the published 16 November x86-64 and
    17 November ARM64 ISOs in QEMU 10.2 on Linux, using these command lines
    (ARM64 emulated with -cpu cortex-a72, as no ARM64 Linux host was at hand):
    each installed onto the virtual NVMe disk and started from it, and the
    x86-64 system reached the internet. A VirtIO disk is not seen on x86-64;
    without bootindex, OVMF kept the boot order saved while starting the ISO and
    never reached the installed disk. The UTM settings are UTM's own defaults,
    read from its source (Configuration/*.swift, main, 17 November 2026); the
    Intel Mac defaults (q35, virtio-vga, e1000, IDE/SATA) were booted in QEMU and
    the Installer offered the SATA disk. UTM itself was not run."""
    dl = s.url('downloads/#system')
    body = '<aside class="note"><strong>What to expect.</strong> A virtual machine is the quickest way to try air/OS, but it isn’t the hardware air/OS is tuned for. The desktop is drawn by the processor, without graphics acceleration, and the GPU, video and NPU features on the ' + s.link(s.url('hardware/'), 'hardware page') + ' don’t apply. The desktop, the apps and the network work as they do on a PC.</aside>'

    body += '<section class="guide" id="image"><h2>Pick the image</h2>'
    body += table(['Your computer', 'Image', 'Runs as'], [
        ['Linux PC with an Intel or AMD processor; Intel Mac', s.link(dl, 'x86-64 ISO'), 'Virtualized: close to native speed'],
        ['Mac with Apple silicon (M1 and later); ARM64 Linux machine', s.link(dl, 'ARM64 ISO'), 'Virtualized: close to native speed'],
        ['Any other combination', 'Either', 'Emulated: works, but several times slower'],
    ])
    body += '<p>Download the image and its SHA-256 file from the ' + s.link(dl, 'downloads page') + ', check it, and unpack it. The Raspberry Pi and Cubie images are for those boards and don’t start in a virtual machine.</p>'
    body += pre("""# Linux
sha256sum -c airos-x86_64.iso.xz.sha256
xz -dk airos-x86_64.iso.xz

# macOS (brew install xz first)
shasum -a 256 -c airos-arm64.iso.xz.sha256
xz -dk airos-arm64.iso.xz""")
    body += '<p>On a Mac without Homebrew, unpack the <code>.xz</code> file with Keka or The Unarchiver instead. Give the virtual machine at least <strong>4 GB of memory</strong>, <strong>2 to 4 processor cores</strong> and a <strong>32 GB disk</strong>.</p></section>'

    body += '<section class="guide" id="qemu"><h2>QEMU on Linux</h2>'
    body += '<p>Install QEMU and its UEFI firmware. On Debian and Ubuntu:</p>'
    body += pre('sudo apt install qemu-system-x86 qemu-system-arm qemu-utils ovmf qemu-efi-aarch64')
    body += '<p>Fedora calls the firmware packages <code>edk2-ovmf</code> and <code>edk2-aarch64</code>; Arch Linux calls them <code>edk2-ovmf</code> and <code>edk2-aarch64</code> as well, with QEMU in <code>qemu-full</code>. The firmware file paths below are Debian’s and Ubuntu’s; elsewhere, look under <code>/usr/share/edk2/</code>. To use KVM, add yourself to the <code>kvm</code> group, then log out and in again.</p>'
    body += '<h3 id="qemu-x86">x86-64</h3>'
    body += '<p>Make a disk and a copy of the firmware’s settings, then start the installer:</p>'
    body += pre("""qemu-img create -f qcow2 airos.qcow2 32G
cp /usr/share/OVMF/OVMF_VARS_4M.fd airos-vars.fd

qemu-system-x86_64 -machine q35 -accel kvm -cpu host -m 4G -smp 4 \\
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd \\
  -drive if=pflash,format=raw,file=airos-vars.fd \\
  -drive if=none,id=disk,file=airos.qcow2 -device nvme,drive=disk,serial=airos,bootindex=1 \\
  -cdrom airos-x86_64.iso \\
  -device qemu-xhci -device usb-tablet \\
  -nic user,model=virtio-net-pci \\
  -audio pa,model=hda \\
  -vga std""")
    body += '<h3 id="qemu-arm64">ARM64</h3>'
    body += '<p>The ARM64 machine has no CD drive, so the ISO goes on a virtual USB stick. The firmware files must be 64 MB, which Debian’s are:</p>'
    body += pre("""qemu-img create -f qcow2 airos.qcow2 32G
cp /usr/share/AAVMF/AAVMF_VARS.fd airos-vars.fd

qemu-system-aarch64 -machine virt -accel kvm -cpu host -m 4G -smp 4 \\
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/AAVMF/AAVMF_CODE.fd \\
  -drive if=pflash,format=raw,file=airos-vars.fd \\
  -drive if=none,id=disk,file=airos.qcow2 -device nvme,drive=disk,serial=airos,bootindex=1 \\
  -device qemu-xhci -device usb-kbd -device usb-tablet \\
  -drive if=none,id=iso,format=raw,readonly=on,file=airos-arm64.iso \\
  -device usb-storage,drive=iso \\
  -nic user,model=virtio-net-pci \\
  -device ramfb""")
    body += '<p>To run the ARM64 image on an Intel or AMD PC, replace <code>-accel kvm -cpu host</code> with <code>-cpu cortex-a72</code>. QEMU then emulates the processor: it works, but starting takes a few minutes.</p>'
    body += '<h3 id="qemu-install">Install and start from the disk</h3><ol class="steps">'
    body += '<li>air/OS starts from the ISO and asks for your language and keymap. Choose <strong>Install air/OS</strong> (or <strong>Try air/OS</strong> to look around first).</li>'
    body += '<li>In the Installer, choose the 32 GB <strong>QEMU NVMe Ctrl</strong> disk under <strong>Erase a whole disk and set it up for UEFI</strong> in the <strong>Onto</strong> menu, click <strong>Begin</strong>, then <strong>Erase disk and install</strong>. The Installer partitions the disk, sets it up for UEFI and copies the system.</li>'
    body += '<li>When it finishes, click <strong>Restart</strong>. <code>bootindex=1</code> makes the firmware try the NVMe disk first, so air/OS now starts from it even with the ISO still attached. (While the disk is empty, the firmware skips it and starts the ISO.) Drop the ISO from the command whenever you like: <code>-cdrom airos-x86_64.iso</code>, or the two lines naming <code>airos-arm64.iso</code>.</li></ol>'
    body += '<p>Click inside the window to use the mouse; <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>G</kbd> releases it. <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>F</kbd> toggles full screen. The network uses QEMU’s built-in address translation: air/OS reaches the internet, but other computers can’t reach it.</p></section>'

    body += '<section class="guide" id="utm"><h2>UTM on a Mac</h2>'
    body += '<p>' + s.link('https://mac.getutm.app/', 'UTM ↗') + ' is a free virtual machine app for macOS built on QEMU. Use the ARM64 ISO on a Mac with Apple silicon and the x86-64 ISO on an Intel Mac.</p>'
    body += '<h3 id="utm-create">Create the virtual machine</h3><ol class="steps">'
    body += '<li>Open UTM, click <strong>+</strong> (<strong>Create a New Virtual Machine</strong>) and choose <strong>Virtualize</strong>, then <strong>Other</strong>.</li>'
    body += '<li>Under <strong>Boot ISO Image</strong>, click <strong>Browse</strong> and choose the unpacked <code>airos-arm64.iso</code> (or <code>airos-x86_64.iso</code> on an Intel Mac). Continue.</li>'
    body += '<li>Set <strong>Memory</strong> to 4096 MB and <strong>CPU Cores</strong> to 4. Leave hardware OpenGL acceleration off. Continue.</li>'
    body += '<li>Set the disk to 32 GB. Continue, and skip <strong>Shared Directory</strong>.</li>'
    body += '<li>On the summary, name the machine “air/OS”, tick <strong>Open VM Settings</strong> and click <strong>Save</strong>.</li></ol>'
    body += '<h3 id="utm-settings">Check the settings</h3>'
    body += '<p>On a Mac with Apple silicon, UTM’s defaults for Other need two changes before the first start; on an Intel Mac, the defaults work as they are.</p>'
    body += table(['Setting', 'Apple silicon (ARM64)', 'Intel Mac (x86-64)'], [
        ['<strong>Display</strong> → Emulated Display Card', 'Change to <strong>ram framebuffer standalone device (ramfb)</strong>', '<code>virtio-vga</code> (the default)'],
        ['The 32 GB drive (under <strong>Drives</strong>) → Interface', 'Change from VirtIO to <strong>NVMe</strong>', 'IDE (the default; air/OS sees it as a SATA disk)'],
        ['<strong>Network</strong> → Emulated Network Card', '<code>virtio-net-pci</code> (the default)', '<code>Intel Gigabit Ethernet (e1000)</code> (the default)'],
        ['<strong>QEMU</strong> → UEFI Boot', 'On (the default)', 'On (the default)'],
    ])
    body += '<p>Click <strong>Save</strong>, then start the machine with ▶︎. It starts from the ISO: install as in <a href="#qemu-install">Install and start from the disk</a>, choosing the 32 GB disk (<strong>QEMU NVMe Ctrl</strong> on Apple silicon, <strong>QEMU HARDDISK</strong> on an Intel Mac). When the Installer has finished, don’t click Restart: shut air/OS down from the Deskbar menu (<strong>Shutdown…</strong> → <strong>Power off</strong>), then in UTM’s window select the CD/DVD drive and choose <strong>Clear</strong>: UTM starts the drives in the order they are listed, so with the ISO still attached it would start the installer again.</p>'
    body += '<p>UTM captures the mouse when you click in the window; press <kbd>Control</kbd>+<kbd>Option</kbd> to release it.</p></section>'

    body += '<section class="guide" id="trouble"><h2>If something goes wrong</h2><ul class="checks">'
    body += '<li><strong>The Installer doesn’t list the disk.</strong> The virtual disk probably uses the VirtIO interface: air/OS, like Haiku, has no VirtIO disk driver on x86-64. Use NVMe as above (SATA works too).</li>'
    body += '<li><strong>A black screen on a Mac with Apple silicon.</strong> Check that the display card is <code>ramfb</code>, the display these instructions were checked with. Display cards with their own video memory, such as VGA, generally don’t work in ARM64 virtual machines on Apple silicon.</li>'
    body += '<li><strong>The firmware tries the network (“Start PXE over IPv4”) or opens a UEFI shell.</strong> It didn’t find a disk to start. Before installing, check that the ISO is attached. After installing in QEMU, check that the disk has <code>bootindex=1</code>: without it, the firmware can keep the boot order it saved while starting the ISO and never reach the disk.</li>'
    body += '<li><strong>It started, then stopped in the kernel debugger.</strong> ' + s.link(s.url('report/'), 'Report an issue') + ' with the virtual machine’s settings and, if you can, the serial output (QEMU: add <code>-serial file:serial.log</code>).</li>'
    body += '</ul></section>'

    toc = [('image', 'Pick the image'), ('qemu', 'QEMU on Linux'), ('qemu-install', 'Install and start'), ('utm', 'UTM on a Mac'), ('utm-settings', 'UTM settings'), ('trouble', 'If something goes wrong')]
    doc_page(s, 'docs/virtualization/', 'Virtualization', 'Run air/OS in a virtual machine: QEMU on Linux, and UTM on a Mac with Apple silicon or an Intel processor.',
             'Documentation · Virtualization', 'air/OS in a virtual machine.',
             'Try air/OS without a spare computer. The x86-64 and ARM64 ISOs start in QEMU on Linux and in UTM on a Mac, and install onto a virtual disk.', toc, body, tabs=False)


# ---------------------------------------------------------------- installation

def installation(s):
    """Installing air/OS, platform by platform: a selector of five guides.

    Sources, all in airos-works/haiku: the Installer (src/apps/installer and
    docs/airos/INSTALLER.md: whole-disk UEFI installs, partition installs,
    Tools menu), First-Boot Setup (docs/rpi4/INSTALLER.md), the Pi boot notes
    (docs/rpi4/BOOT.md, docs/rpi5/BOOT.md and STATUS.md), the ROCK 5 ITX
    firmware notes (docs/rock5-itx/RECOVERY.md: EDK2 v1.1 in SPI, device tree
    only), the Dragon Q8B notes (docs/dragon-q8b/STATUS.md) and the Cubie SD
    image (tools/cubie-a7s/build-sd-image.sh). The EFI loader opens its menu
    on Space or Esc (platform/efi/console.cpp). The Intel Mac guide was
    tried on a 2017 iMac (iMac18,1) with the 21 November 2026 release; its
    expectations for other Macs follow from the drivers' coverage."""
    images = {im['target']: im for im in json.loads((s.root / 'data/github.json').read_text())['images']}
    downloads = s.url('downloads/#system')
    write = s.url('downloads/write/')

    def image_name(target):
        im = images.get(target) or {'assets': []}
        asset = next((a for a in im['assets'] if a['name'].endswith(('.iso.xz', '.img.xz'))), None)
        return asset, im

    def download(target, label):
        asset, im = image_name(target)
        if not asset:
            return f'<div class="install-download">{s.link(downloads, "Get the " + label + " from the downloads page →", "button primary")}</div>'
        extras = ''.join(s.link(a['browser_download_url'], 'SHA-256' if a['name'].endswith('.sha256') else 'Build manifest')
                         for a in sorted(im['assets'], key=lambda a: a['name'] == 'manifest.json')
                         if a['name'].endswith('.sha256') or a['name'] == 'manifest.json')
        return (f'<div class="install-download">{s.link(asset["browser_download_url"], "Download the " + label + " ↓", "button primary")}'
                f'<p class="meta"><code>{e(asset["name"])}</code> · {asset['size'] / 1e9:.1f} GB compressed · built {im["published"][:10]}</p>'
                f'<p class="install-extras">{extras}{s.link(downloads, "All downloads")}</p></div>')

    def name(target, fallback):
        asset, _ = image_name(target)
        return asset['name'] if asset else fallback

    def step(id, n, title, body):
        return f'<section class="guide" id="{id}"><h3><span class="step-number">{n}</span>{title}</h3>{body}</section>'

    def write_commands(file, medium, mac_only=False):
        mac = f"""# macOS: find the {medium} by its size, then use its disk number N
diskutil list external
shasum -a 256 -c {file}.sha256
diskutil unmountDisk /dev/diskN
xz -dc {file} | sudo dd of=/dev/rdiskN bs=4m
diskutil eject /dev/diskN"""
        linux = f"""# Linux: find the {medium} by its size and model, then use its whole device
lsblk -o NAME,SIZE,MODEL,TRAN
sha256sum -c {file}.sha256
sudo umount /dev/sdX?*
xz -dc {file} | sudo dd of=/dev/sdX bs=4M conv=fsync oflag=direct status=progress
sync"""
        html = '<p>Put the image and its SHA-256 file in one folder, check the download, and write the image to the <strong>whole</strong> ' + medium + '. Writing erases everything on it.</p>'
        if mac_only:
            html += pre(mac)
            html += '<p>macOS has no <code>xz</code>: install it with Homebrew (<code>brew install xz</code>), or unpack the image with Keka or The Unarchiver and write it with <code>sudo dd if=airos-x86_64.iso of=/dev/rdiskN bs=4m</code>. Press <kbd>Ctrl</kbd>+<kbd>T</kbd> to see progress. If macOS then says the disk isn’t readable, choose <strong>Ignore</strong> or <strong>Eject</strong>, never <strong>Initialize</strong>.</p>'
        else:
            html += pre(linux + '\n\n' + mac)
            html += '<p><strong>Windows:</strong> unpack the <code>.xz</code> file with 7-Zip, open the unpacked image in Rufus and, when Rufus asks, choose <strong>Write in DD Image mode</strong>.</p>'
        html += f'<p>Double-check the device: <code>dd</code> overwrites whatever disk you name. Don’t use balenaEtcher, which has silently damaged an air/OS image. {s.link(write, "The full guide to writing an image")}, with Windows step by step and how to check the copy →</p>'
        return html

    first_start = '<p>air/OS starts and asks for your language and keymap. Choose <strong>Try air/OS</strong> to look around first (the Installer is on the Desktop and in Deskbar’s Applications menu), or <strong>Install air/OS</strong>.</p>'

    def whole_disk(loader, disk_hint):
        return ('<ol>'
                '<li>The Installer opens with a short notice. Click <strong>Continue</strong>.</li>'
                f'<li>Open the <strong>Onto</strong> menu. Under <strong>Erase a whole disk and set it up for UEFI</strong>, each disk is listed with its model, size, path and the volumes on it. {disk_hint} Disks it can’t use, such as the one air/OS is running from, are listed but greyed out, with the reason.</li>'
                '<li>Click <strong>Begin</strong>. The Installer names the disk and its volumes once more: click <strong>Erase disk and install</strong>. (<strong>Cancel</strong> is the default, so pressing <kbd>Enter</kbd> erases nothing.)</li>'
                f'<li>The Installer writes a new GUID partition map with a 512 MiB EFI system partition and a Be File System partition named <code>airOS</code> over the rest, copies the system, and puts its UEFI loader at <code>EFI/BOOT/{loader}</code>, the path firmware starts from a disk without needing a boot entry.</li>'
                '<li>When it says the installation is complete, click <strong>Restart</strong> and remove the USB stick as the screen goes dark.</li></ol>')

    partition_steps = ('<li>Start air/OS from the USB stick and open the Installer. Choose <strong>Tools → Set up partitions…</strong> to open DriveSetup.</li>'
                       '<li>Select the empty space (or the partition you made for air/OS, after checking its size, and choose <strong>Partition → Delete</strong>). Choose <strong>Partition → Create…</strong>, set the type to <strong>Be File System</strong>, name it <code>airOS</code>, and click <strong>Create</strong>. Then choose <strong>Partition → Format → Be File System</strong> and confirm. Close DriveSetup.</li>'
                       '<li>In the Installer’s <strong>Onto</strong> menu, choose the new partition under <strong>Install onto an existing partition</strong> and click <strong>Begin</strong>.</li>')

    # ---- x86-64 PC
    x86 = name('x86_64', 'airos-x86_64.iso.xz')
    pc = '<div class="section-heading"><h2>An Intel or AMD PC.</h2><span>x86-64 ISO · USB stick</span></div>'
    pc += '<p class="section-lead">The x86-64 ISO starts from a USB stick on UEFI and older BIOS PCs. The Installer then erases a disk and sets it up to start with UEFI, or installs onto a partition you prepared.</p>'
    pc += step('pc-need', 1, 'What you need', '<ul class="checks">'
               '<li>A 64-bit Intel or AMD PC with at least 4 GB of memory. There is no 32-bit image.</li>'
               '<li>A USB stick of 8 GB or more.</li>'
               '<li>A disk for air/OS of 32 GB or more: an NVMe or SATA drive, or an external USB disk. Installing onto a whole disk erases it.</li>'
               '<li>A wired keyboard and mouse, at least for the first start: Bluetooth ones work only once paired in air/OS.</li>'
               f'<li>A look at the {s.link(s.url("hardware/"), "hardware notes")}. Graphics acceleration is for the tested AMD and NVIDIA cards; elsewhere the desktop uses the frame buffer the firmware set up.</li></ul>')
    pc += step('pc-write', 2, 'Download the ISO and write the USB stick', download('x86_64', 'x86-64 ISO') + write_commands(x86, 'USB stick'))
    pc += step('pc-start', 3, 'Start from the stick', '<ol>'
               '<li>Open the firmware settings (usually <kbd>F2</kbd> or <kbd>Del</kbd> as the PC starts) and turn off <strong>Secure Boot</strong>: the air/OS loader isn’t signed. If the SATA mode is RAID or Intel RST, set it to <strong>AHCI</strong> so air/OS sees the drive (Windows on that drive may need its own preparation first).</li>'
               '<li>Insert the stick, restart and open the boot menu: commonly <kbd>F12</kbd> (Dell, Lenovo, Framework, Gigabyte), <kbd>F11</kbd> (MSI, ASRock), <kbd>F8</kbd> (ASUS) or <kbd>F9</kbd> (HP). Choose the stick, its <strong>UEFI:</strong> entry if it has two.</li></ol>' + first_start)
    pc += step('pc-install', 4, 'Install onto a whole disk', whole_disk('BOOTX64.EFI', 'Pick the disk for air/OS by its model and size.') +
               '<p>If the PC goes back to another system, choose the disk in the boot menu, or move it to the top of the boot order in the firmware settings.</p>')
    pc += step('pc-alongside', 5, 'Or install alongside another system', '<p>To keep Windows or Linux on the same disk, give air/OS a partition of its own. Back up first.</p><ol>'
               '<li>Make at least 32 GB of free space: in Windows, Disk Management → right-click the volume → <strong>Shrink Volume</strong>; in Linux, GParted. Leave the space unallocated.</li>'
               + partition_steps +
               '<li>Then choose <strong>Tools → Install EFI loader</strong> and pick the disk’s existing EFI system partition. The loader goes to <code>EFI/BOOT/BOOTX64.EFI</code>; if one is already there (Windows keeps a copy), the Installer offers to rename it. Windows still starts from its own boot entry.</li>'
               '<li>Restart and choose the disk in the firmware’s boot menu, often listed as <strong>UEFI OS</strong> or by the disk’s name. If it lists only Windows Boot Manager, add an entry for <code>\\EFI\\BOOT\\BOOTX64.EFI</code> in the firmware settings.</li></ol>'
               '<p><strong>A PC without UEFI</strong> (most made before 2012) starts the ISO in BIOS mode but can’t start a disk set up for UEFI. In DriveSetup, choose the disk and <strong>Disk → Initialize → Intel Partition Map</strong> (this erases it), create a Be File System partition and install onto it as above. The Installer writes the partition’s boot sector; then use <strong>Tools → Set up boot menu…</strong> to write a boot menu to the disk. This is Haiku’s own BIOS method; it hasn’t been retested on air/OS.</p>')
    pc += step('pc-trouble', 6, 'If something goes wrong', '<ul class="checks">'
               '<li><strong>The stick isn’t in the boot menu, or the PC ignores it.</strong> Check that Secure Boot is off, try another USB port, and write the stick again with <code>dd</code> or Rufus in DD mode.</li>'
               '<li><strong>“No boot volume found”.</strong> The copy is damaged: check it and write it again.</li>'
               '<li><strong>A black screen after the boot logo.</strong> Restart and press <kbd>Space</kbd> as air/OS starts to open its boot menu, choose <strong>Select safe mode options</strong> → <strong>Use fail-safe graphics driver</strong>, then <strong>Continue booting</strong>.</li>'
               '<li><strong>The Installer doesn’t list the drive.</strong> Set the SATA mode to AHCI, as above. A drive behind a RAID controller isn’t supported.</li></ul>')

    # ---- ARM64 with UEFI
    arm = name('arm64', 'airos-arm64.iso.xz')
    a64 = '<div class="section-heading"><h2>An ARM64 machine with UEFI.</h2><span>ARM64 ISO · USB stick</span></div>'
    a64 += '<p class="section-lead">The ARM64 ISO starts on ARM64 boards and computers with UEFI firmware. It is installed and tested on the Radxa ROCK 5 ITX and the Radxa Dragon Q8B. It doesn’t start the Raspberry Pi or the Cubie A7S, which have SD card images of their own.</p>'
    a64 += step('arm64-need', 1, 'What you need', '<ul class="checks">'
                '<li>The board, with UEFI firmware (step 2).</li>'
                '<li>A USB stick of 8 GB or more.</li>'
                '<li>A disk for air/OS of 32 GB or more: an NVMe SSD on both boards, or an SD card on the Dragon Q8B. The ROCK 5 ITX’s eMMC is listed too.</li>'
                '<li>An HDMI monitor, a USB keyboard and mouse, and an Ethernet cable for the first start.</li></ul>')
    a64 += step('arm64-firmware', 2, 'Check the firmware', table(['Board', 'Firmware', 'Settings'], [
        ['<strong>ROCK 5 ITX</strong>', 'EDK2 UEFI for the RK3588 (' + s.link('https://github.com/edk2-porting/edk2-rk3588', 'edk2-rk3588 ↗') + ') in the board’s SPI flash; release v1.1 is the one tested. Its README explains how to write it to the flash.',
         'In the firmware setup (<kbd>Esc</kbd> at the splash): <strong>Device Manager → Rockchip Platform Configuration → ACPI / Device Tree</strong>, set the configuration table mode to <strong>Device Tree</strong> and the device tree compatibility to <strong>Mainline</strong>, the settings air/OS was tested with.'],
        ['<strong>Dragon Q8B</strong>', 'Radxa’s UEFI firmware, as the board comes.', 'None. It tries USB, then the SD card, then the NVMe.'],
        ['Other ARM64 UEFI machines', 'UEFI with a device tree or ACPI tables.', 'Untested: they may start, with fewer drivers.'],
    ]) + '<p>On the ROCK 5 ITX, installing Radxa’s Debian through ROOBI replaces EDK2 in the SPI flash with U-Boot, and writing EDK2 again resets its settings: set them again afterwards.</p>')
    a64 += step('arm64-write', 3, 'Download the ISO and write the USB stick', download('arm64', 'ARM64 ISO') + write_commands(arm, 'USB stick'))
    a64 += step('arm64-start', 4, 'Start from the stick', '<p>Insert the stick into a USB port and switch the board on. The Dragon Q8B starts from USB by itself. On the ROCK 5 ITX, press <kbd>Esc</kbd> at the splash, choose <strong>Boot Manager</strong> and then the stick (<strong>UEFI</strong> followed by its name).</p>' + first_start)
    a64 += step('arm64-install', 5, 'Install onto the NVMe or SD card', whole_disk('BOOTAA64.EFI', 'Pick the NVMe SSD (or, on the Dragon Q8B, the SD card) by its size.') +
                '<p>The Dragon Q8B starts the new disk as soon as no bootable USB stick is attached. On the ROCK 5 ITX, if EDK2 starts an older system instead (a boot entry made for an earlier installation stops matching once the disk is erased), open <strong>Boot Maintenance Manager → Boot Options → Change Boot Order</strong> and move the drive (<strong>UEFI</strong> followed by the SSD’s model) to the top.</p>')
    a64 += step('arm64-trouble', 6, 'If something goes wrong', '<ul class="checks">'
                '<li><strong>The ROCK 5 ITX stops right after the loader.</strong> Check the device tree settings in step 2: EDK2’s defaults return whenever the firmware is written again.</li>'
                '<li><strong>The firmware menus don’t react to the keyboard.</strong> Plug it into another USB port, directly rather than through a hub or KVM: some firmware can’t use composite USB devices.</li>'
                '<li><strong>It started, then stopped in the kernel debugger.</strong> ' + s.link(s.url('report/'), 'Report an issue') + ' with the board and the firmware version.</li></ul>')

    # ---- Raspberry Pi
    rpi = name('rpi4', 'airos-rpi4.img.xz')
    pi = '<div class="section-heading"><h2>Raspberry Pi 4 and Pi 5.</h2><span>Raspberry Pi image · SD card</span></div>'
    pi += '<p class="section-lead">One SD card image starts both the Pi 4 and the Pi 5. The card is the installation: write it, start the Pi from it, and First-Boot Setup gives air/OS the rest of the card.</p>'
    pi += step('pi-need', 1, 'What you need', '<ul class="checks">'
               '<li>A Raspberry Pi 4 Model B or Raspberry Pi 5. Both were tested with 4 GB of memory; the Pi 400, Pi 500 and Compute Modules haven’t been tried.</li>'
               '<li>A microSD card of 16 GB or more; 32 GB or more, rated A1 or A2, is better.</li>'
               '<li>The official power supply: 5.1 V, 3 A USB-C for the Pi 4; 27 W (5 A) USB-C for the Pi 5.</li>'
               '<li>A micro-HDMI cable and a monitor, a USB keyboard and mouse, and Ethernet or Wi-Fi. A heatsink or fan helps under load: air/OS doesn’t control the Pi 5’s fan yet.</li></ul>')
    pi += step('pi-write', 2, 'Download the image and write the SD card', download('rpi4', 'Raspberry Pi image') + write_commands(rpi, 'SD card'))
    pi += step('pi-start', 3, 'Start the Pi', '<ol>'
               '<li>Insert the card. Connect the monitor <strong>before</strong> switching on: on the Pi 4 use <strong>HDMI0</strong>, the micro-HDMI port next to the USB-C power port; on the Pi 5 either port works. A monitor connected later stays dark until a restart.</li>'
               '<li>Plug in the keyboard and mouse (on the Pi 5, the blue USB 3 ports are fastest) and the power. The first start takes about a minute.</li></ol>')
    pi += step('pi-setup', 4, 'First-Boot Setup', '<p>On the first start, First-Boot Setup opens on the desktop.</p><ol>'
               '<li><strong>Step 1, storage:</strong> it shows the card’s current and available size. Choose to use the entire card and confirm; the partition table is changed and checked, and air/OS grows into the space at the next start. Or keep the current size.</li>'
               '<li><strong>Step 2, time zone:</strong> choose yours. The Pi has no clock that keeps time while it’s off (the Pi 5’s isn’t supported yet), so air/OS sets the time from the network.</li>'
               '<li>Click <strong>Restart now</strong>. Setup doesn’t appear again; to change your choice later, open <strong>Applications → First-Boot Setup</strong>.</li></ol>')
    pi += step('pi-usb', 5, 'Pi 5: start from a USB disk instead', '<p>The Pi 5 also starts the same image from a USB SSD or stick: write it as above, plug it into a blue USB 3 port and remove the SD card. With a supply that isn’t the 5 A one, the Pi 5 refuses to start from USB unless <code>config.txt</code> has <code>usb_max_current_enable=1</code> in its <code>[pi5]</code> section. That file is on the disk’s first partition, which Windows, macOS and Linux can open.</p>')
    pi += step('pi-trouble', 6, 'If something goes wrong', '<ul class="checks">'
               '<li><strong>No picture.</strong> On the Pi 4, use HDMI0, connect the monitor before switching on, and restart.</li>'
               '<li><strong>The Pi doesn’t start, or stops with a lightning bolt.</strong> Use the official supply: an undersized one makes the board throttle or reset, especially with USB disks attached.</li>'
               f'<li><strong>Not yet supported:</strong> NVMe HATs on the Pi 5’s PCIe connector, sound HATs, the power button and choosing a resolution in Screen preferences. The {s.link(s.url("hardware/#rpi5"), "hardware notes")} list the rest.</li></ul>')

    # ---- Cubie A7S
    cub = name('cubie', 'airos-cubie.img.xz')
    cubie = '<div class="section-heading"><h2>Radxa Cubie A7S.</h2><span>Cubie image · SD card</span></div>'
    cubie += '<p class="section-lead">The Cubie A7S starts air/OS from a microSD card that carries Radxa’s boot chain. As on the Raspberry Pi, the card is the installation; the generic ARM64 ISO doesn’t start this board.</p>'
    cubie += step('cubie-need', 1, 'What you need', '<ul class="checks">'
                  '<li>A Radxa Cubie A7S.</li>'
                  '<li>A microSD card of 16 GB or more; 32 GB or more, rated A1 or A2, is better.</li>'
                  '<li>A USB-C power supply that meets Radxa’s recommendation for the board, a monitor, and a USB keyboard and mouse (a small USB hub helps).</li>'
                  '<li>A heatsink: cooling matters under sustained load. The onboard Wi-Fi joins 5 GHz WPA2 networks.</li></ul>')
    cubie += step('cubie-write', 2, 'Download the image and write the SD card', download('cubie', 'Cubie A7S image') + write_commands(cub, 'SD card'))
    cubie += step('cubie-start', 3, 'Start the board', '<p>Insert the card, connect the monitor, keyboard and mouse, then the power. The board starts Radxa’s boot loader from the card, which starts air/OS’s own U-Boot, which starts air/OS.</p>')
    cubie += step('cubie-setup', 4, 'First-Boot Setup', '<p>First-Boot Setup opens on the desktop, as on the Raspberry Pi: <strong>Step 1</strong> offers to use the entire card (the card’s boot chain and EFI partition are left as they are), <strong>Step 2</strong> sets the time zone, then <strong>Restart now</strong>. It is in <strong>Applications → First-Boot Setup</strong> afterwards. Keep the card in the board: it is where air/OS is installed.</p>')
    cubie += step('cubie-trouble', 5, 'If something goes wrong', '<ul class="checks">'
                  '<li><strong>Nothing on the screen.</strong> Check the copy and write the card again with <code>dd</code> or Rufus in DD mode: the boot chain sits in the first 16 MB of the card, and a tool that copies files instead of the raw image leaves it out.</li>'
                  '<li><strong>The system slows down under load.</strong> Check the cooling.</li>'
                  f'<li>Bluetooth pairing and audio over Bluetooth aren’t verified yet; see the {s.link(s.url("hardware/#cubie"), "hardware notes")}.</li></ul>')

    # ---- Intel Mac
    # What was tested comes from the 2017 iMac (iMac18,1) in the lab, on the
    # 21 November 2026 releases (airos-works/haiku d8118d62ea, eadea8ae2e,
    # 4be9e78620, 6a10a3b24b, d7eefef711, e7d4fcf6c0, b9c5be6d8e, 542e09df45;
    # linux-drm's i915_drm). The other rows follow from the drivers' coverage:
    # broadcomfmac's PCI table, nvme_disk's class probe, i915_drm (Gen 9 on),
    # amdgpu_drm (Tonga on), nouveau_drm (before Maxwell), bge and ixgbe.
    mac = ('<aside class="note caution"><strong>Tested on one Mac so far.</strong> air/OS installs and runs on a 21.5-inch iMac from 2017: '
           'what works on it is listed below. Other Intel Macs haven’t been tried yet. Step 1 says what to expect from the parts in them. Please '
           + s.link(s.url('report/'), 'report what you find') + ', including what worked.</aside>')
    mac += '<div class="section-heading"><h2>A Mac with an Intel processor.</h2><span>x86-64 ISO · USB stick</span></div>'
    mac += ('<p class="section-lead">Intel Macs have UEFI firmware, so the x86-64 ISO starts on them as it does on a PC. Use an image from 21 November 2026 or later: '
            'older images don’t start on a Mac, or can’t install onto an SSD with 4 KiB sectors such as the iMac’s. The safest first installation goes onto an external disk, which leaves macOS untouched.</p>')
    mac += ('<section class="guide" id="mac-tested"><h3>Tested: iMac (21.5-inch, 2017)</h3>'
            '<p>The lab’s iMac18,1 has a dual-core Core i5-7360U, 8 GB of memory, Intel Iris Plus Graphics 640 and a 256 GB SSD. It runs the 21 November 2026 release, installed from the USB stick onto the whole internal SSD, and every driver comes from the image: nothing was added by hand.</p>'
            + table(['Part', 'On the 2017 iMac'], [
                ['Starting up', 'Startup Manager (<kbd>Option</kbd> at power-on) shows the USB stick and the installed SSD with the air/OS icon. The boot menu (<kbd>Space</kbd>) and the start-up messages (<kbd>Esc</kbd>) show on screen.'],
                ['Installing', 'A whole-disk install onto the internal SSD (an Apple SSD SM0256L, with 4 KiB sectors), which then starts on its own. It replaced macOS.'],
                ['Graphics', 'Iris Plus Graphics 640 through Linux’s i915 driver: the built-in 1920 × 1080 screen with a hardware cursor, OpenGL 4.6 (GLTeapot at about 2,000 frames per second), Vulkan 1.4, and hardware H.264, HEVC and VP9 decoding and encoding.'],
                ['Wi-Fi', 'Broadcom BCM43602: scanning, joining a WPA2 network, about 300 Mbit/s down and 100 Mbit/s up, and joining it again at start-up.'],
                ['Ethernet', 'Broadcom BCM57766 at 1 Gbit/s.'],
                ['Sound', 'Cirrus Logic CS8409: the built-in speakers and the built-in microphone.'],
                ['Bluetooth', 'The built-in Broadcom radio finds nearby devices; an Apple Wireless Keyboard pairs and types.'],
                ['Also working', 'USB keyboards, mice and disks on the USB-A ports; Windows (SMB) network shares; restarting, including the automatic restart after a crash.'],
                ['Not tried yet', 'The headphone jack, the FaceTime HD camera (it is listed as a video source), the SD card slot, the Thunderbolt 3 ports, an external display, screen brightness and sleep.'],
            ]) + '</section>')
    mac += step('mac-which', 1, 'Check your Mac', '<p>What air/OS can drive depends on the chips inside, which changed every few years. This is what to expect, from the drivers air/OS has and from the parts each Mac shares with the tested iMac. Only the 2017 iMac has actually been run.</p>' + table(['Mac', 'Graphics', 'What to expect'], [
        ['<strong>iMac (2017)</strong><br>iMac18,1–18,3',
         '21.5-inch: Iris Plus 640, tested. Retina 4K and 5K: Radeon Pro 555–580 (Polaris), the same design as the tested Radeon Pro WX 5100 in a PC, through amdgpu; not tried on a Mac.',
         'Tested on the iMac18,1. The Retina models have the same Wi-Fi, sound and Bluetooth, and should behave the same.'],
        ['<strong>MacBook Pro (2016–2017)</strong><br>MacBookPro13,1–14,3',
         'Intel HD 530–630, Iris 540–550 and Iris Plus 640–650 (Skylake, Kaby Lake) through i915, like the iMac. 15-inch: also Radeon Pro 450–560 (Polaris), through amdgpu.',
         'The same Wi-Fi (BCM43602) and sound (CS8409) as the iMac. The built-in keyboard and trackpad are connected over SPI, which air/OS has no driver for: use USB ones. The SSD has Apple’s own controller, which probably isn’t seen: install onto an external disk. Every port is Thunderbolt 3: plug the stick and keyboard in before power-on. The Touch Bar stays dark.'],
        ['<strong>MacBook (12-inch, 2015–2017)</strong><br>MacBook8,1–10,1',
         '2015: HD 5300 (Broadwell), without acceleration. 2016–2017: HD 515 and HD 615 through i915.',
         'Its BCM4350 Wi-Fi is in the driver but untried. SPI keyboard and trackpad and Apple’s own SSD controller, as on the 2016–2017 MacBook Pro. The one USB-C port needs a hub for the stick, a keyboard and a mouse.'],
        ['<strong>iMac (2019)</strong><br>iMac19,1–19,2',
         'Radeon Pro 555X–580X (Polaris) and Vega 48, through amdgpu; not tried on a Mac.',
         'The same CS8409 sound as the 2017 iMac. Check the Wi-Fi chip (below).'],
        ['<strong>2013–2015:</strong> MacBook Air (2013–2017), MacBook Pro (late 2013–2015), iMac (late 2013–2015), Mac mini (2014), Mac Pro (2013)',
         'Intel HD 5000 to Iris Pro 6200 (Haswell, Broadwell): Haiku’s intel_extreme sets the screen mode, without acceleration. NVIDIA GeForce GT 750M–GTX 780M (Kepler): nouveau, tested on a desktop Kepler card, not a Mac. AMD: the R9 M295X and M395X (Tonga) are in amdgpu’s range; other Radeons and the Mac Pro’s FirePro stay on Haiku’s radeon_hd or the firmware’s frame buffer.',
         'Most have Broadcom BCM4360 Wi-Fi, which isn’t supported: use Ethernet or a USB Ethernet adapter. The laptops’ keyboards and trackpads are USB devices and should work, the trackpad as a plain mouse. Sound uses Haiku’s HD Audio driver; untried.'],
        ['<strong>2011–2012:</strong> MacBook Air, MacBook Pro, iMac and Mac mini',
         'Intel HD 3000 and HD 4000: intel_extreme, without acceleration. Radeon HD 6000M (2011): radeon_hd or the frame buffer. GeForce GT 640M–GTX 680MX (2012, Kepler): nouveau, untried on a Mac.',
         'Broadcom BCM4331 Wi-Fi isn’t supported. Keyboards and trackpads as on the 2013–2015 laptops. These Macs’ older firmware hasn’t been tried at all.'],
        ['<strong>Mac Pro (2010–2012)</strong><br>MacPro5,1',
         'A graphics card from the ' + s.link(s.url('hardware/'), 'hardware page') + ' is accelerated as in a PC. Startup Manager shows on screen only with a card that has Mac or UEFI firmware.',
         'Its Intel gigabit Ethernet has a driver. Wi-Fi as on the 2011–2012 Macs.'],
        ['<strong>Macs with the T2 chip:</strong> iMac Pro, iMac 27-inch (2020), Mac mini (2018), Mac Pro (2019), MacBook Air (2018–2020) and MacBook Pro (2018–2020)',
         'Intel UHD 617–630 and Iris Plus 645–655 (Gen 9): i915. Radeon Pro, from the 555X to the W6900X (Polaris, Vega, RDNA): amdgpu. The 2020 MacBook Air’s and four-port 13-inch MacBook Pro’s Ice Lake graphics: i915 with <code>haiku_probe all</code> in its settings, untried.',
         'Need the security changes in step 3. The T2 handles the internal SSD, sound, the camera and, on the laptops, the keyboard and trackpad: none of these work, so install onto an external disk and use USB input devices. Their Wi-Fi (BCM4364, BCM4377) isn’t supported. Gigabit Ethernet and the Mac Pro’s Intel 10-gigabit ports should work; the Aquantia 10-gigabit port of the iMac Pro (an option on the Mac mini and 2020 iMac) has no driver.'],
        ['<strong>The first Intel Macs (2006–2007)</strong>', '—',
         'Many have 32-bit EFI and can’t start the 64-bit loader.'],
        ['<strong>Macs with Apple silicon</strong> (M1 and later)', '—',
         'Can’t start air/OS: run it in ' + s.link(s.url('docs/virtualization/#utm'), 'UTM') + ' instead.'],
    ]) + '<p><strong>Which parts are in yours.</strong> <strong>Apple menu → About This Mac → More Info → System Report</strong> gives the model identifier and the graphics; note them for a report. In Terminal, <code>ioreg -l -p IODeviceTree | grep firmware-abi</code> should print <code>EFI64</code>, and <code>ioreg -r -n ARPT | grep device-id</code> names the Wi-Fi chip on most Intel Macs: <code>&lt;ba430000&gt;</code> is the tested BCM43602; <code>&lt;a3430000&gt;</code> (BCM4350) and <code>&lt;ec430000&gt;</code> (BCM4356) are in the driver but untried; others, such as <code>&lt;a0430000&gt;</code> (BCM4360) and <code>&lt;31430000&gt;</code> (BCM4331), aren’t supported.</p>'
       '<p><strong>Graphics without a driver</strong> still work: air/OS shows the desktop on the frame buffer the firmware set up, at the screen’s resolution, without acceleration. On a 15-inch MacBook Pro with two GPUs, the built-in screen stays on the GPU the firmware chose, and air/OS doesn’t switch between them.</p>')
    mac += step('mac-need', 2, 'What you need', '<ul class="checks">'
                '<li>A USB stick of 8 GB or more (with an adapter on a Mac that has only USB-C).</li>'
                '<li>A <strong>wired USB keyboard and mouse</strong>. Apple’s wireless keyboards, mice and trackpads use Bluetooth: they work in the Mac’s startup menu, but in air/OS only once paired in its Bluetooth preferences. On a MacBook or MacBook Pro from 2015 on, the built-in keyboard and trackpad don’t work.</li>'
                '<li>An <strong>Ethernet cable</strong> (or a USB Ethernet adapter), unless the Mac has the BCM43602 Wi-Fi of the 2017 iMac and the 2016–2017 MacBook Pro. Most other Intel Macs have Broadcom Wi-Fi that air/OS has no driver for.</li>'
                '<li>An external SSD or disk of 32 GB or more for the recommended installation, or 32 GB of free space on the internal disk.</li>'
                '<li>A current Time Machine backup.</li></ul>')
    mac += step('mac-prepare', 3, 'Prepare the Mac', '<ul class="checks">'
                '<li><strong>Macs with the T2 chip:</strong> restart holding <kbd>⌘</kbd>+<kbd>R</kbd> to open macOS Recovery, then choose <strong>Utilities → Startup Security Utility</strong>. Set Secure Boot to <strong>No Security</strong> and External Boot to <strong>Allow booting from external or removable media</strong>.</li>'
                '<li><strong>A firmware password</strong>, if set, is asked for when you choose a startup disk. Have it ready.</li>'
                '<li>Other Intel Macs need no changes.</li></ul>')
    mac += step('mac-write', 4, 'Download the ISO and write the USB stick in macOS', download('x86_64', 'x86-64 ISO') + write_commands(x86, 'USB stick', mac_only=True))
    mac += step('mac-start', 5, 'Start from the stick', '<ol>'
                '<li>Shut the Mac down. Plug in the stick, the wired keyboard and mouse, and Ethernet.</li>'
                '<li>Press the power button, then at once press and hold <kbd>Option</kbd> (<kbd>⌥</kbd>; <kbd>Alt</kbd> on a PC keyboard) until Startup Manager shows the startup disks.</li>'
                '<li>Choose <strong>EFI Boot</strong>, the stick with the air/OS icon, and press <kbd>Return</kbd>.</li></ol>'
                + first_start +
                '<p>Choose <strong>Try air/OS</strong> the first time and check the screen, keyboard, mouse, network and sound before installing.</p>')
    mac += step('mac-external', 6, 'Install onto an external disk (recommended)', whole_disk('BOOTX64.EFI', 'Pick the external disk by its model and size. The internal disk is the one with macOS’s volumes, such as <code>Macintosh HD</code>: don’t choose it.') +
                '<p>To start air/OS, hold <kbd>Option</kbd> at power-on and choose <strong>EFI Boot</strong> on the external disk. Without it, the Mac starts macOS as before.</p>')
    mac += step('mac-alongside', 7, 'Or install alongside macOS on the internal disk', '<p>Don’t do this on an iMac or Mac mini with a <strong>Fusion Drive</strong> (an SSD and a hard disk that macOS joins into one): air/OS sees them as two disks, and changing either breaks the pair. Use an external disk instead.</p><ol>'
                '<li>In macOS, open Disk Utility and choose <strong>View → Show All Devices</strong>. Select the internal disk itself (the top line), click <strong>Partition</strong>, then <strong>+</strong>, and choose <strong>Add Partition</strong> (not Add Volume). Name it <code>AIROS</code>, choose the <strong>MS-DOS (FAT)</strong> format and a size of 32 GB or more, and click <strong>Apply</strong>. macOS shrinks its own partition to make room.</li>'
                + partition_steps.replace('the partition you made for air/OS', 'the <code>AIROS</code> partition you made in macOS') +
                '<li>Choose <strong>Tools → Install EFI loader</strong> and pick the internal disk’s EFI partition (about 200 MB, named <code>EFI</code>). This puts the loader at <code>EFI/BOOT/BOOTX64.EFI</code>, a path macOS doesn’t use. If a Boot Camp installation of Windows already put a loader there, the Installer offers to rename it.</li>'
                '<li>Restart holding <kbd>Option</kbd>: <strong>EFI Boot</strong> starts air/OS and <strong>Macintosh HD</strong> starts macOS, which stays the default.</li></ol>'
                '<p>To remove air/OS later, delete its partition in macOS’s Disk Utility and let macOS take the space back.</p>'
                '<p><strong>The whole internal disk</strong> can be used too, with the whole-disk option above, as on the tested iMac. That erases macOS and its Recovery partition: macOS can then be reinstalled only through Internet Recovery (<kbd>⌥</kbd>+<kbd>⌘</kbd>+<kbd>R</kbd> at power-on).</p>')
    mac += step('mac-trouble', 8, 'If something goes wrong', '<ul class="checks">'
                '<li><strong>Startup Manager shows no EFI Boot.</strong> Write the stick again with <code>dd</code> and try another port. On a T2 Mac, check that external booting is allowed (step 3). A Mac with 32-bit EFI can’t start it.</li>'
                '<li><strong>The air/OS splash stays on screen, or the screen goes black.</strong> Check that the image is from 21 November 2026 or later. Then start again and press <kbd>Space</kbd> repeatedly as air/OS starts, to open its boot menu: choose <strong>Select safe mode options</strong> → <strong>Use fail-safe graphics driver</strong>, then <strong>Continue booting</strong>. To see where it stops, press <kbd>Esc</kbd> instead: air/OS shows its start-up messages, and a photo of the last lines helps a report.</li>'
                '<li><strong>The Installer says the partitions could not be formatted.</strong> The disk has 4 KiB sectors, like the 2017 iMac’s SSD: use an image from 21 November 2026 or later.</li>'
                '<li><strong>The keyboard or mouse doesn’t react in air/OS.</strong> Use wired USB ones, plugged into the Mac directly. On MacBooks from 2015 on and on T2 Macs, the built-in keyboard and trackpad never do.</li>'
                '<li><strong>No network.</strong> Use Ethernet, unless the Mac’s Wi-Fi chip is one that works (step 1).</li>'
                '<li><strong>Whatever happens, please tell us.</strong> ' + s.link(s.url('report/'), 'Report an issue') + ' with the model identifier, the graphics, how far it got and, if it reached the desktop, <code>/var/log/syslog</code>.</li></ul>')

    platforms = [
        ('pc', 'x86-64 PC', 'Intel and AMD desktops and laptops, UEFI or BIOS.', pc),
        ('arm64', 'ARM64 with UEFI', 'Radxa ROCK 5 ITX, Dragon Q8B and other UEFI machines.', a64),
        ('raspberry-pi', 'Raspberry Pi', 'Pi 4 and Pi 5, from one SD card.', pi),
        ('cubie-a7s', 'Cubie A7S', 'Radxa’s Allwinner A733 board, from an SD card.', cubie),
        ('intel-mac', 'Intel Mac', 'iMac, Mac mini, MacBook and Mac Pro with an Intel processor. Tested on a 2017 iMac.', mac),
    ]
    # Without JavaScript these are jump links and every guide is shown; site.js
    # turns them into tabs, as on the apps page.
    tabs = '<nav class="app-tabs platform-tabs" aria-label="Platforms" data-app-tabs>'
    tabs += ''.join(f'<a href="#{id}" data-tab="{id}"><strong>{label}</strong><span>{summary}</span></a>' for id, label, summary, _ in platforms)
    tabs += '</nav>'
    panels = ''.join(f'<section id="{id}" class="tab-panel install-panel">{body}</section>' for id, _, _, body in platforms)
    lead = 'Choose the computer you’re installing on. Each guide goes from the download to a system that starts on its own: writing the USB stick or SD card, starting from it, and installing.'
    html = s.intro('Documentation · Installation', 'Install air/OS.', lead, wide=True)
    html += '<aside class="note"><strong>Before you start.</strong> air/OS is a development build: back up anything on the disk you install onto. Every image can be tried live before installing, and you can also run air/OS in a ' + s.link(s.url('docs/virtualization/'), 'virtual machine') + ' without touching a disk.</aside>'
    html += tabs + f'<div class="doc-layout no-toc"><div class="doc-body install-body">{panels}</div></div>'
    s.page('docs/install/', 'Installation', 'Install air/OS on an x86-64 PC, an ARM64 machine with UEFI, a Raspberry Pi 4 or 5, a Radxa Cubie A7S or an Intel Mac: writing the USB stick or SD card, starting from it and installing.', html)


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
    installation(s)
    virtualization(s)
