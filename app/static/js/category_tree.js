// creating dynamic selector Category
function setAttributes(el, attrs, text = undefined) {
  for (var key in attrs) {
    el.setAttribute(key, attrs[key]);
  }
  if (text) { el.innerText = text; }
};

const hidden_field = document.getElementById("category-tree-data")
console.log(hidden_field, hidden_field.value)
const data = JSON.parse(hidden_field.value)
console.log(data)
console.log(data.category)

function layout_node(node) {
  const li = document.createElement('li');
  const a = document.createElement('a');
  setAttributes(a, { "href": "#" }, node.category);
  if (node.children.length == 0){
    li.append(a);
  } else {
    const span = document.createElement('span');
    span.setAttribute("class", "caret");
    li.append(span);
    li.append(a);
    const ul = document.createElement('ul');
    setAttributes(ul, { "class": "nested" });
    li.append(ul);
    node.children.forEach(node => {
      ul.append(layout_node(node));
    });
  }
  return li;
};

// define "root category"
const div = document.createElement('div');
const rootUl = document.createElement('ul');
const rootLi = document.createElement('li');
const rootSpan = document.createElement('span');
const rootA = document.createElement('a');
// define elements of another categories and subcategories

// create tree
div.setAttribute('class', 'testing');
setAttributes(rootUl, { "id": "categoryTreeID", "class": "tree" });
setAttributes(rootLi, { "id": "rootID" });
setAttributes(rootSpan, { "class": "caret" });
setAttributes(rootA, { "href": "#" }, "Root");

// document.querySelector(".category_panel").after(div);
div.append(rootUl);
rootUl.append(rootLi);
rootLi.append(rootSpan);
rootLi.append(rootA);

const ul = document.createElement('ul');
rootLi.append(ul)
setAttributes(ul, { "class": "nested" });

data.children.forEach(node => {
  ul.append(layout_node(node));
});


let toggler = document.getElementsByClassName("caret");

for (let i = 0; i < toggler.length; i++) {
  toggler[i].addEventListener("click", function () {
    this.parentElement.querySelector(".nested").classList.toggle("active");
    this.classList.toggle("caret-down");
  });
}

// save configuration for categories
const root = document.getElementById("rootID")
const textRoot = root.querySelector("a")
const category = document.getElementById("categoryTreeID")
const subcategories = Array.from(category.getElementsByTagName("a"))
console.log(subcategories)
let previusActiveLink = root
subcategories.forEach(el => {
  console.log(el.innerText);
  el.addEventListener("click", (event) => {
    const currentLink = event.path[1]
    previusActiveLink.classList.remove("active_link");
    previusActiveLink = currentLink
    currentLink.classList.add("active_link");
    if (currentLink === root) {
      el.innerText = data.category
    } else { textRoot.innerText = `${el.innerText}` };
  })
});
