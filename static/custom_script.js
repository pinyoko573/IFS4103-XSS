window.onload = function () {
    let obj = window.someObject || {};
    let script = document.createElement('script');
    script.src = obj.url;
    if (obj.url != undefined) document.body.appendChild(script);
}