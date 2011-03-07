$(function() {
    $("#filetypeselect").change(function(){
        switch($("#filetypeselect option:selected").first().val()){
            case("mat"):
                $("#addoption").empty();
                $("#addoption").append("<dt>MATLAB variable name</dt><dd><input type=text name=matvar></dd>");
                break;
            case("csv"):
                $("#addoption").empty();
                $("#addoption").append("<dt>delimeter</dt><dd><input type=text name=delim></dd>");
                break;
        }
    }).trigger('change');
});
