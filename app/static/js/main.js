// custom javascript
// test js (need refracting)
const hidden_field = document.getElementById("hidden_field_id")
hidden_field.setAttribute("value", "Json")
console.log(hidden_field, hidden_field.value)

// const root = document.getElementById("rootID")
// const textRoot = root.querySelector("a")
// const category = document.getElementById("categoryTreeID")
// const subcategories = Array.from(category.getElementsByTagName("a"))
// console.log(subcategories)
// let previusActiveLink = root
// subcategories.forEach(el => {
//     console.log(el.innerText);
//     el.addEventListener("click", (event) => {
//         const currentLink = event.path[1]
//         previusActiveLink.classList.remove("active_link");
//         previusActiveLink = currentLink
//         currentLink.classList.add("active_link");
//         if (currentLink === root) {
//             el.innerText = "Root"
//         } else {textRoot.innerText = `${el.innerText}`};
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
function setAttributes(el, attrs, text=undefined) {
    for (var key in attrs) {
      el.setAttribute(key, attrs[key]);
    }
    if (text) {el.innerText = text;}
};

// define "root category"
const categoryPanel = document.querySelector(".category_panel");
const div = document.createElement('div');
const rootUl = document.createElement('ul');
const rootLi = document.createElement('li');
const rootSpan = document.createElement('span');
const rootA = document.createElement('a');
// define elements of another categories and subcategories
const ul = document.createElement('ul');
const li = document.createElement('li');
const span = document.createElement('span');
const a = document.createElement('a');

// create tree
div.setAttribute('class', 'testing');
setAttributes(rootUl, {"id": "categoryTreeID", "class": "tree"});
setAttributes(rootLi, {"id": "rootID"});
setAttributes(rootSpan, {"class": "caret"});
setAttributes(rootA, {"href": "#"}, "Root");

setAttributes(ul, {"class": "nested"});


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
categoryPanel.after(div);
div.append(rootUl);
rootUl.append(rootLi);
rootLi.append(rootSpan);
rootSpan.append(rootA);

rootLi.append(ul)
