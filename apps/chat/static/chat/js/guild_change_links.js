function copy(el) {
    let $tmp = $("<input>");
    $("body").append($tmp);
    $tmp.val(http_protocol + '://' + $(el).text()).select();
    document.execCommand("copy");
    $tmp.remove();
}