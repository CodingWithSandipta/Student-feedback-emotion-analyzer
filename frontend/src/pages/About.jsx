import { Brain, Database, Code, BookOpen, AlertTriangle, Github } from 'lucide-react'
import { SectionHeader } from '../components/UI'

function Section({ icon: Icon, title, children, iconColor = 'text-indigo-600' }) {
  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-9 h-9 rounded-xl bg-indigo-50 flex items-center justify-center ${iconColor}`}>
          <Icon className="w-5 h-5" />
        </div>
        <h2 className="text-lg font-bold text-slate-800">{title}</h2>
      </div>
      {children}
    </div>
  )
}

function Tag({ children, color = 'bg-indigo-50 text-indigo-700' }) {
  return <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium mr-1 mb-1 ${color}`}>{children}</span>
}

export default function About() {
  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <SectionHeader
        title="About This Project"
        subtitle="Academic deep learning project documentation"
      />

      {/* Project overview */}
      <Section icon={Brain} title="Project Overview">
        <div className="prose prose-sm text-slate-600 leading-relaxed space-y-3">
          <p>
            <strong className="text-slate-800">AI-Based Student Feedback Emotion Analyzer</strong> is an academic
            project that uses a Bidirectional Long Short-Term Memory (Bi-LSTM) neural network to automatically
            classify the emotional tone and sentiment of student feedback submitted to educational institutions.
          </p>
          <p>
            The system helps college administrators and teachers gain quantitative insights into student opinions
            about teaching quality, faculty behavior, infrastructure, examinations, and other academic dimensions.
          </p>
          <p>
            This project was developed as a demonstration of applied Natural Language Processing (NLP) and deep
            learning in an educational analytics context.
          </p>
        </div>
      </Section>

      {/* Architecture */}
      <Section icon={Brain} title="Bi-LSTM Architecture">
        <div className="space-y-4">
          <div className="bg-slate-900 text-slate-300 rounded-xl p-5 font-mono text-xs space-y-1">
            <p className="text-slate-500">Input Text</p>
            <p className="pl-4 text-green-400">↓ Text Cleaning & Normalization</p>
            <p className="pl-4 text-green-400">↓ Keras Tokenizer (vocab: 20,000)</p>
            <p className="pl-4 text-green-400">↓ Sequence Padding (maxlen: 100)</p>
            <p className="pl-4 text-yellow-400">↓ Embedding Layer (dim: 128)</p>
            <p className="pl-4 text-blue-400">↓ Bidirectional LSTM (64 units × 2 directions)</p>
            <p className="pl-4 text-purple-400">↓ Dropout (0.3)</p>
            <p className="pl-4 text-yellow-400">↓ Dense Layer (64, ReLU)</p>
            <p className="pl-4 text-purple-400">↓ Dropout (0.3)</p>
            <p className="pl-4 text-green-400">↓ Softmax Output (7 classes)</p>
            <p className="text-slate-500">Output: Emotion Probabilities</p>
          </div>
          <div className="text-sm text-slate-600">
            <strong className="text-slate-700">Why Bidirectional LSTM?</strong> A standard LSTM processes text
            left-to-right, potentially missing right-context information. A Bi-LSTM processes the sequence
            in both directions simultaneously, allowing the model to capture context from both preceding
            and following words — particularly useful for emotion-laden phrases that depend on context.
          </div>
        </div>
      </Section>

      {/* Dataset */}
      <Section icon={BookOpen} title="Dataset: GoEmotions">
        <div className="space-y-3 text-sm text-slate-600">
          <div className="flex items-start gap-2 bg-amber-50 border border-amber-100 rounded-xl p-3">
            <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
            <p className="text-amber-700 text-xs">
              <strong>Important Disclaimer:</strong> GoEmotions is a dataset of Reddit comments — not a student feedback dataset.
              It is used as a training source for emotion classification due to its size and annotation quality.
              Predictions on real student feedback may differ due to domain mismatch.
            </p>
          </div>
          <ul className="space-y-2">
            <li>📊 <strong>Source:</strong> Google Research — GoEmotions</li>
            <li>🔗 <strong>Access:</strong> HuggingFace datasets (<code className="bg-slate-100 px-1 rounded">go_emotions</code>)</li>
            <li>🏷️ <strong>Original labels:</strong> 28 emotion categories (multi-label)</li>
            <li>🗂️ <strong>Mapped to:</strong> 7 target classes (documented mapping)</li>
            <li>🎯 <strong>Split:</strong> 70% train / 15% validation / 15% test (stratified)</li>
            <li>⚖️ <strong>Class balance:</strong> Handled via class weights</li>
          </ul>
          <div className="mt-3">
            <p className="font-medium text-slate-700 mb-2">Emotion Mapping (GoEmotions → Our Taxonomy):</p>
            <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-3 rounded-xl">
              <div><strong>Joy:</strong> joy, amusement, excitement</div>
              <div><strong>Satisfaction:</strong> approval, admiration, gratitude, love, optimism, relief, pride</div>
              <div><strong>Anger:</strong> anger, disgust</div>
              <div><strong>Sadness:</strong> sadness, grief, disappointment, remorse</div>
              <div><strong>Fear:</strong> fear, nervousness</div>
              <div><strong>Frustration:</strong> annoyance</div>
              <div><strong>Neutral:</strong> neutral</div>
            </div>
          </div>
        </div>
      </Section>

      {/* Technology stack */}
      <Section icon={Code} title="Technology Stack">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Machine Learning</p>
            {['TensorFlow / Keras', 'Bidirectional LSTM', 'scikit-learn', 'NumPy', 'Pandas', 'Matplotlib', 'Seaborn', 'HuggingFace datasets'].map(t => (
              <Tag key={t} color="bg-purple-50 text-purple-700">{t}</Tag>
            ))}
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Backend</p>
            {['Python 3.11', 'Flask 3.0', 'Flask-CORS', 'SQLAlchemy', 'SQLite', 'REST API'].map(t => (
              <Tag key={t} color="bg-blue-50 text-blue-700">{t}</Tag>
            ))}
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Frontend</p>
            {['React 18', 'Vite', 'Tailwind CSS', 'Recharts', 'Lucide Icons', 'React Router', 'Axios'].map(t => (
              <Tag key={t} color="bg-green-50 text-green-700">{t}</Tag>
            ))}
          </div>
        </div>
      </Section>

      {/* Limitations */}
      <Section icon={AlertTriangle} title="Known Limitations" iconColor="text-amber-500">
        <ul className="space-y-2 text-sm text-slate-600">
          <li className="flex items-start gap-2">
            <span className="text-amber-500 mt-0.5">⚠</span>
            <span>The model is trained on general conversational Reddit text, not domain-specific student feedback.</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-500 mt-0.5">⚠</span>
            <span>Confidence scores represent softmax output probabilities — not calibrated prediction accuracy.</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-500 mt-0.5">⚠</span>
            <span>Short feedback (fewer than 10 words) may produce less reliable predictions.</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-500 mt-0.5">⚠</span>
            <span>This is a local academic demonstration system, not a production data management platform.</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-500 mt-0.5">⚠</span>
            <span>No real student PII should be stored; student IDs are optional and anonymized in public views.</span>
          </li>
        </ul>
      </Section>

      {/* Quick start */}
      <Section icon={Database} title="Quick Start Guide">
        <div className="space-y-3">
          <div className="bg-slate-900 text-slate-300 rounded-xl p-4 font-mono text-xs space-y-2">
            <p className="text-slate-500"># 1. Set up Python virtual environment</p>
            <p>python -m venv venv</p>
            <p className="text-slate-500 mt-2"># 2. Install backend dependencies</p>
            <p>cd backend && pip install -r requirements.txt</p>
            <p className="text-slate-500 mt-2"># 3. Train the model (requires internet)</p>
            <p>python train_model.py</p>
            <p className="text-slate-500 mt-2"># 4. Start the backend API</p>
            <p>python app.py</p>
            <p className="text-slate-500 mt-2"># 5. Start the frontend (new terminal)</p>
            <p>cd frontend && npm install && npm run dev</p>
          </div>
          <p className="text-xs text-slate-400">
            Or simply run <code className="bg-slate-100 px-1 rounded">start_project.bat</code> (Windows) or
            <code className="bg-slate-100 px-1 rounded ml-1">start_project.sh</code> (Linux/macOS).
          </p>
        </div>
      </Section>
    </div>
  )
}
