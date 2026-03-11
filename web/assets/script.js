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

// Countdown Timers
var electionDate = new Date("November 7, 2026 00:00:00").getTime();
var enrolmentDate = new Date("October 25, 2026 00:00:00").getTime();
var switchingRollsDate = new Date("August 6, 2026 00:00:00").getTime();
var votingOpensDate = new Date("October 26, 2026 00:00:00").getTime();

// Update countdown timers every second
setInterval(function () {
  var now = new Date().getTime();
  var electionTimeLeft = electionDate - now;
  var enrolmentTimeLeft = enrolmentDate - now;
  var switchingRollsTimeLeft = switchingRollsDate - now;
  var votingOpensTimeLeft = votingOpensDate - now;

  // Update the countdown display
  document.querySelectorAll("#election-day").forEach(function(element) {
    element.innerText = formatTimeLeft(electionTimeLeft);
  });
  document.querySelectorAll("#enrol-date").forEach(function(element) {
    element.innerText = formatTimeLeft(enrolmentTimeLeft);
  });
  document.querySelectorAll("#switch-rolls-date").forEach(function(element) {
    element.innerText = formatTimeLeft(switchingRollsTimeLeft);
  });
  document.querySelectorAll("#voting-opens-date").forEach(function(element) {
    element.innerText = formatTimeLeft(votingOpensTimeLeft);
  });
}, 1000);

// Format time left as a string
function formatTimeLeft(timeLeft) {
  var days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
  var hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
  return days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
}

// Share button functionality
document.addEventListener('DOMContentLoaded', () => {

  document.getElementById('share-btn').addEventListener('click', async () => {
    if (navigator.share) {
      try {
        // Fetch the image and convert to a File object
        const response = await fetch('https://nzpt.cjs.nz/assets/nzptshare.png');
        const blob = await response.blob();
        const file = new File([blob], 'nzptshare.png', { type: 'image/png' });

        // Check the browser can share files before trying
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({
            title: 'NZPolToolbox – Urgency Tracker',
            text: 'Check out the latest NZ Parliament urgency statistics. #nzpol',
            url: 'https://nzpt.cjs.nz',
            files: [file]
          });
        } else {
          // Browser supports sharing but not files — share without image
          await navigator.share({
            title: 'NZPolToolbox – Urgency Tracker',
            text: 'Check out the latest NZ Parliament urgency statistics. #nzpol via NZPT',
            url: 'https://nzpt.cjs.nz'
          });
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          // AbortError just means the user cancelled — ignore it
          console.error('Share failed:', err);
        }
      }
    } else {
      // Fallback for Firefox desktop etc.
      await navigator.clipboard.writeText('https://nzpt.cjs.nz');
      alert('Link copied to clipboard!');
    }
  });
});