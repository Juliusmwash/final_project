function pdfShowBox() {
  const animatedBox = document.querySelector('.pdf-download-container');
  animatedBox.classList.add('visible');
}
function pdfHideBox() {
  const animatedBox = document.querySelector('.pdf-download-container');
  animatedBox.classList.remove('visible');
}

const downloadPdfButton = document.querySelector('.download-pdf-button');
downloadPdfButton.addEventListener('click', () => {
  // Change background color
  pdfGetRandomColor();

  document.querySelector('.font-size-box').style.display = 'none';
  pdfShowBox();
});
const pdfExitBtn = document.getElementById('pdf-exit-btn');
pdfExitBtn.addEventListener('click', () => {
  const defaultBtn = document.querySelector('.pdf-download-btn');
  defaultBtn.style.display = "flex";
  const advancedBox = document.querySelector('.advanced-box');
  advancedBox.style.display = "none";
  pdfHideBox()
});

const advancedBtn = document.getElementById('advanced-btn');
advancedBtn.addEventListener('click', () => {
  // Change background
  pdfGetRandomColor();

  const advancedBox = document.querySelector('.advanced-box');
  const defaultBtn = document.querySelector('.pdf-download-btn');
  advancedBox.style.display = advancedBox.style.display == "flex"? "none" : "flex";
  if (advancedBox.style.display === "flex") {
    defaultBtn.style.display = "none";
  } else {
    defaultBtn.style.display = "flex";
  }
});

const defaultBtn = document.querySelector('.pdf-download-btn');
defaultBtn.addEventListener('click', () => {
  const defaultFormBtn = document.getElementById('default-pdf-form');
  defaultFormBtn.submit();
});

const downloadAdvancedBtn = document.getElementById('download-advanced-btn');
downloadAdvancedBtn.addEventListener('click', () => {
  const customPdfForm = document.getElementById("custom-pdf-form");
  customPdfForm.submit();
});


// Function to randomly select a color code
function pdfGetRandomColor() {
  // Array of color codes
  const colorArray = ["#253529", "#3b3c36", "#414a4c", "#232B2B", "#123524", "#1A2421", "#674846", "#704241", "#000036", "#000039", "#253529", "#32174d", "#100C08", "#080808", "#1c2841", "#480607", "#010127", "#151922", "#004242"];

  let randomIndex = Math.floor(Math.random() * colorArray.length);
  const advancedBox = document.querySelector('.advanced-box');
  const defaultBtn = document.querySelector('.pdf-download-btn');
  const advancedBtn = document.getElementById('advanced-btn');
  const dwdAdvcdBtn = document.getElementById('download-advanced-btn');

  const color = colorArray[randomIndex];

  advancedBox.style.backgroundColor = color
  defaultBtn.style.backgroundColor = color
  advancedBtn.style.backgroundColor = color

  randomIndex = Math.floor(Math.random() * colorArray.length);
  dwdAdvcdBtn.style.backgroundColor = colorArray[randomIndex];
}
