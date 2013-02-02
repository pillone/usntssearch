function fn() { //function that sometimes takes a long time
    show_loader();    
}
function show_loader() {
    document.getElementById('loader').style.visibility = "visible";
}
function hide_loader() {
    document.getElementById('loader').style.visibility = "hidden";
}
 
