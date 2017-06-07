/**
 * Created by zc on 2017/4/6.
 */
String.prototype.format=function()
{
  if(arguments.length==0) return this;
  for(var s=this, i=0; i<arguments.length; i++)
    s=s.replace(new RegExp("\\{"+i+"\\}","g"), arguments[i]);
  return s;
};

$(document).ready(function () {
    var fixHelperModified = function (e, tr) {
            var $originals = tr.children();
            var $helper = tr.clone();
            $helper.children().each(function (index) {
                $(this).width($originals.eq(index).width())
            });
            return $helper;
        },
        updateIndex = function (e, ui) {
            $('td.index', ui.item.parent()).each(function (i) {
                $(this).html(i + 1);
            });
            // fillAguments()
        };
    $("#id_case tbody").sortable({
        helper: fixHelperModified,
        stop: updateIndex
    }).disableSelection();
    $("#id_case").tablesorter();
    $('#id_case').on("DOMSubtreeModified", function(){fillAguments();})
    fillAguments();
});

function getAguments() {
    var env_id = $("#id_test_environment").val();
    var env_name = $("#id_test_environment").find("option:selected").text();
    var title = $("#id_report_title").val();
    var description = $("#id_report_description").val();
    var rows = $("#id_case").find("tr").length - 1;
    var aguments = {
        "test_environment":{
            "id": env_id,
            "name": env_name
        },
        "title":title,
        "description":description,
        "case":[]
    }
    for(var i=0;i<rows;i++){
        var case_id = $("#id_case tbody tr:eq({0})".format(i)).find("td").eq(0).text()
        var case_name =$("#id_case tbody tr:eq({0})".format(i)).find("td").eq(1).text()
        var case_json={"id":case_id,"name":case_name}
        aguments.case.push(case_json)
    }
    var aguments_str = JSON.stringify(aguments,null,4)
    return (aguments_str)
}

function fillAguments(){
    var aguments = getAguments()
    $("#id_arguments").html(aguments)
}