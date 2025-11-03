const API_BASE = "";
let quiz = null;

async function loadQuiz() {
  const storedQuiz = localStorage.getItem("latestQuiz");

  if (!storedQuiz) {
    document.getElementById("result").innerText =
      "No hay formulario guardado en el navegador.";
    return;
  }

  quiz = JSON.parse(storedQuiz);
  if (typeof quiz === "string") {
    quiz = quiz.replace(/```json|```/g, "").trim();

    try {
      quiz = JSON.parse(quiz);
    } catch (err) {
      console.error("Error al parsear el quiz:", err);
      document.getElementById("result").innerText =
        "Error al interpretar el formulario.";
      return;
    }
  }

  if (Array.isArray(quiz)) {
    quiz = { questions: quiz };
  }

  renderQuiz(quiz);
}

function renderQuiz(quiz) {
  if (!quiz || !quiz.questions) {
    console.log("Quiz data is invalid:", quiz);
    document.getElementById("result").innerText =
      "No se pudo cargar el formulario.";
    return;
  }

  const form = document.getElementById("quiz-form");
  form.innerHTML = "";

  quiz.questions.forEach((q, i) => {
    const div = document.createElement("div");
    div.classList.add("question-block", "mb-3", "p-3", "border", "rounded");

    const p = document.createElement("p");
    p.innerText = `${i + 1}. ${q.question}`;
    div.appendChild(p);

    q.options.forEach((opt) => {
      const label = document.createElement("label");
      label.classList.add("form-check-label", "d-block", "mb-1");

      const input = document.createElement("input");
      input.type = "radio";
      input.name = `q${i}`;
      input.value = opt;
      input.classList.add("form-check-input", "me-2");

      label.appendChild(input);
      label.append(opt);
      div.appendChild(label);
    });

    form.appendChild(div);
  });
}

document.getElementById("submit-quiz").addEventListener("click", () => {
  if (!quiz || !quiz.questions) {
    alert("No hay preguntas cargadas.");
    return;
  }

  const form = document.getElementById("quiz-form");
  const answers = {};
  let score = 0;

  quiz.questions.forEach((q, i) => {
    const selected = form.querySelector(`input[name="q${i}"]:checked`);
    const userAnswer = selected ? selected.value : null;
    answers[`q${i}`] = userAnswer;

    const options = form.querySelectorAll(`input[name="q${i}"]`);

    options.forEach((opt) => {
      const label = opt.parentElement;
      label.classList.remove("text-success", "text-danger", "fw-bold");

      // Si es la correcta
      if (opt.value === q.answer) {
        label.classList.add("text-success", "fw-bold");
      }

      // Si el usuario eligió mal
      if (userAnswer && opt.value === userAnswer && userAnswer !== q.answer) {
        label.classList.add("text-danger", "fw-bold");
      }
    });

    if (userAnswer === q.answer) score++;
  });

  document.getElementById(
    "result"
  ).innerText = `Tu puntaje: ${score} / ${quiz.questions.length}`;
});

window.onload = loadQuiz;
