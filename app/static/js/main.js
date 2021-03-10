// custom javascript
// test js (need refracting)
const hidden_field = document.getElementById("hidden_field_id")
hidden_field.setAttribute("value", "Json")
console.log(hidden_field, hidden_field.value)

// const root = document.getElementById("rootID")
// const category = document.getElementById("categorySelectorID")
// const subcategories = Array.from(category.getElementsByTagName("a"))
// console.log(subcategories)
// let previusActiveLink = root
// subcategories.forEach(el => {
//     console.log(el.innerText);
//     el.addEventListener("click", () => {
//         previusActiveLink.classList.remove("active_link");
//         previusActiveLink = el
//         el.classList.add("active_link");
//         if (el === root) {
//             root.innerText = "Root"
//         } else {root.innerText = `${el.innerText}`}
//     })
// });
// test work tree
let toggler = document.getElementsByClassName("caret");
let i;

for (i = 0; i < toggler.length; i++) {
  toggler[i].addEventListener("click", function() {
    this.parentElement.querySelector(".nested").classList.toggle("active");
    this.classList.toggle("caret-down");
  });
}



// creating dynamic selector Category
function setAttributes(el, attrs) {
    for(var key in attrs) {
      el.setAttribute(key, attrs[key]);
    }
};

const ul = document.createElement('ul');
const li = document.createElement('li');
const a = document.createElement('a');

// div.setAttribute('class', '_form-search');
// img.setAttribute('src', '/static/images/Search_icon.png');
// setAttributes(input, {
//     "class": "input_search",
//     "placeholder": "Search",
//     "aria-controls": "workItemsTable",
//     "id": "customSearchId",
// });
// div.prepend(img);
// div.append(input);
// document.querySelector('.chart-left .form').before(div);
