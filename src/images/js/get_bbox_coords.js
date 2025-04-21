const el = document.getElementById('Text');
const rect = el.getBoundingClientRect();
return {
    top: rect.top,
    left: rect.left,
    width: rect.width,
    height: rect.height
};
