// creating dynamic selector Category

const hidden_field = document.getElementById("category-tree-data");
const g_treeData = JSON.parse(hidden_field.value);
let g_currentSelectedIndex = 0;
console.log(g_treeData);

function getNodeByIndex(index) {
  function getNode(node) {
    if (node.index == index) {
      return node;
    }
    for (let i in node.nodes) {
      let child = node.nodes[i];
      if (child.index == index) {
        return child;
      }
      child = getNode(child);
      if (child) {
        return child;
      }
    }
    return null;
  }
  return getNode(g_treeData);
}

// Treeview Initialization
function getTree() {
  // remove empty nodes
  function removeEmptyNodes(node) {
    if (!node.nodes) return;
    if (node.nodes.length == 0) {
      delete node.nodes;
      return;
    }
    node.nodes.forEach((node) => removeEmptyNodes(node));
  }
  removeEmptyNodes(g_treeData);
  return [g_treeData];
}

function saveData(index) {
  let data = getNodeByIndex(index);
  if (data) {
    data.LEAVE_VIDAXL_PREFIX = $("#LEAVE_VIDAXL_PREFIX").prop("checked");
    data.MOM_SELECTOR = $("#MOM_SELECTOR").prop("checked");
    data.MARGIN_PERCENT = parseFloat($("#MARGIN_PERCENT").val());
    data.ROUND_TO = parseInt($("#ROUND_TO").val(), 10);
  }
}

function loadData(index) {
  let data = getNodeByIndex(index);
  if (data) {
    $("#LEAVE_VIDAXL_PREFIX").prop("checked", data.LEAVE_VIDAXL_PREFIX);
    $("#MOM_SELECTOR").prop("checked", data.MOM_SELECTOR);
    $("#MARGIN_PERCENT").val(data.MARGIN_PERCENT);
    $("#ROUND_TO").val(data.ROUND_TO);
  }
}

$("#category-tree").treeview({
  // expandIcon: "glyphicon glyphicon-checked",
  // collapseIcon: "glyphicon glyphicon-unchecked",
  // collapseIcon: "glyphicon glyphicon-unchecked",
  data: getTree(),
  onNodeSelected: function (event, node) {
    loadData(node.index);
    g_currentSelectedIndex = node.index;
  },
  onNodeUnselected: function (event, node) {
    saveData(node.index);
  },
});

$("#category-tree").treeview("selectNode", [0, { silent: true }]);
loadData(0);
$("#submit").click(function () {
  saveData(g_currentSelectedIndex);
  hidden_field.value = JSON.stringify(g_treeData);
});
