/*                                                                               <!-- Generator Box span element color change -->                                 <div id="span-change-color-activator-btn"></div>                                           <div id="span-change-color-btn"></div>                                           <!-- Generator Box span element color change end -->                   */
alert("here");
const buttonOne = document.getElementById('span-change-color-activator-btn');
const buttonTwo = document.getElementById('span-change-color-btn');

buttonTwo.addEventListener('click', () => {
  alert('clicked');
  buttonOne.style.zIndex = 170;
});

buttonOne.addEventListener('click', () => {
  alert('clicked');
  buttonTwo.style.zIndex = 170;
});
