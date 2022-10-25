// functions
function toTitleCase(s) {
  return s.replace(/\w\S*/g, (t) => t.charAt(0).toUpperCase() + t.substr(1));
}

function data2svg(minval, maxval, coef, se) {
  let minmaxScaling = (x) => (500 * (x - minval)) / (maxval - minval); // 500 * (min-max scaling)
  if (coef > 0) {
    return [
      minmaxScaling(0), // coef origin
      minmaxScaling(coef) - minmaxScaling(0), // coef offset
      minmaxScaling(coef - 1.96 * se), // CI
      minmaxScaling(coef + 1.96 * se),
      minmaxScaling(coef), // CI origin
    ];
  } else {
    return [
      minmaxScaling(coef),
      minmaxScaling(0) - minmaxScaling(coef),
      minmaxScaling(coef - 1.96 * se),
      minmaxScaling(coef + 1.96 * se),
      minmaxScaling(coef),
    ];
  }
}

export { toTitleCase, data2svg };
