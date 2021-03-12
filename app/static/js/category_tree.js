// creating dynamic selector Category

const hidden_field = document.getElementById("category-tree-data")
const data = JSON.parse(hidden_field.value)
console.log(data)


// Treeview Initialization
function getTree() {


  return [data];
}

$('#category-tree').treeview({
  expandIcon: "glyphicon glyphicon-unchecked",
  collapseIcon: "glyphicon glyphicon-unchecked",
  // collapseIcon: "glyphicon glyphicon-unchecked",
  data: getTree(),
  onNodeSelected: function (event, node) {
    console.log(`selected ${node.nodeId}`);
    $('#LEAVE_VIDAXL_PREFIX').prop('checked', node.LEAVE_VIDAXL_PREFIX);
    $('#MOM_SELECTOR').prop('checked', node.MOM_SELECTOR);
    $('#MARGIN_PERCENT').val(node.MARGIN_PERCENT);
    $('#ROUND_TO').val(node.ROUND_TO);
  },
  onNodeUnselected: function (event, node) {
    console.log(`unselected ${node.nodeId}`);
    node.LEAVE_VIDAXL_PREFIX = $('#LEAVE_VIDAXL_PREFIX').prop('checked');
    node.MOM_SELECTOR = $('#MOM_SELECTOR').prop('checked');
    node.MARGIN_PERCENT = $('#MARGIN_PERCENT').val();
    node.ROUND_TO = $('#ROUND_TO').val();
  }
});

$('#category-tree').treeview('selectNode', [0, { silent: true }]);
