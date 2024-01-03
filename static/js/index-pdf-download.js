/*
<!-- pdf download section -->                                                                   <div class="pdf-download-container" style="display: none;">                                       <div class="download-box">                                                                        <form action="/generate_pdf_route" method="POST">                                                 <input type="hidden" name="default_pdf" value="okay"/>                                        </form>                                                                                         <button class="pdf-download-btn" type="submit" id="download-btn">download</button>              <span id="advanced-btn">advanced</span>                                                       </div>                                                                                          <div class="advanced-box">                                                                        <form action="/generate_pdf_route" method="POST">                                                 <label class="pdf-input-label">letter spacing</label>                                           <input type="number" class="pdf-input" name="letter_spacing" value=0/>                                                                                                                          <label class="pdf-input-label">font size</label>                                                <input type="number" class="pdf-input" name="font_size" value=0/>                                                                                                                               <label class="pdf-input-label">page margins</label>                                             <input type="number" class="pdf-input" name="page_margins" value=0/>                                                                                                                            <label class="pdf-input-label">background color</label>                                         <input type="number" class="pdf-input" name="background_color" value=0/>                                                                                                                        <label class="pdf-input-label">text colour</label>                                              <input type="number" class="pdf-input" name="text_color" value=0/>
              </form>                                                                                         <button class="pdf-download-btn" type="submit" id="download-advanced-btn">download</button>                                                                                                   </div>                                                                                        </div>                                                                                          <!-- pdf download sectiom end -->
*/


/*
const changeBackgroundBtn = document.getElementById('change-background-btn');                   const backgroundDropdownBox = document.querySelector('.background-dropdown-box');               const backgroundDropdownAll = document.querySelectorAll('.background-dropdown');                                                                                                                changeBackgroundBtn.addEventListener('click', () => {                                             document.querySelector('.background-dropdown-box').style.display = 'flex';                      showBox3();                                                                                     document.querySelector('.font-size-box').style.display = 'none';                              });                                                                                                                                                                                             backgroundDropdownAll.forEach((element) => {                                                      element.addEventListener('click', () => {                                                         choiceBackground = element.getAttribute('data-background-code')                                 document.querySelector('.font-size-box').style.display = 'none';                                hideBox3();                                                                                     document.querySelector('.generator-box').style.backgroundColor = choiceBackground;              document.querySelectorAll('p').forEach((element) => {                                             element.style.color = choiceColor;                                                            });                                                                                           });                                                                                           });                                                                                                                                                                                             */
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
