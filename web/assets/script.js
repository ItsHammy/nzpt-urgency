document.addEventListener("DOMContentLoaded", function () {
    const questions = document.querySelectorAll("#faqs h3");

    questions.forEach((question) => {
      const answer = question.nextElementSibling;

      question.addEventListener("click", () => {
        if (answer.style.display === "block") {
          answer.style.display = "none";
        } else {
          answer.style.display = "block";
        }
      });
    });
  });