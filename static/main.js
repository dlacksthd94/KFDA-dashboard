// functions
toTitleCase = (
  s // make the fisrt letter upper case
) => s.replace(/\w\S*/g, (t) => t.charAt(0).toUpperCase() + t.substr(1));

data2svg = (minval, maxval, coef, se) => {
  conv = (x) => (500 * (x - minval)) / (maxval - minval); // 500 * (min-max scaling)
  if (coef > 0) {
    return [
      conv(0), // coef origin
      conv(coef) - conv(0), // coef offset
      conv(coef - 1.96 * se), // CI
      conv(coef + 1.96 * se),
      conv(coef), // CI origin
    ];
  } else {
    return [
      conv(coef),
      conv(0) - conv(coef),
      conv(coef - 1.96 * se),
      conv(coef + 1.96 * se),
      conv(coef),
    ];
  }
};

// event listener("Generate" button)
$("#generate").click(() => {
  $("#spinner").removeClass("d-none"); // ???

  // get props from filtering options
  if ($("#mode_drug").prop("checked")) mode = "drug";
  else if ($("#mode_meta").prop("checked")) mode = "meta";
  prop = {
    mode: mode + "_chart",
    drug: $("#drug_meta").val(), // the selected drug
    model: $("#drug_model").val(), // the selected model type
    pvalue: $("#drug_pvalue").val(), // the selected p-value type
    meta: $("#meta_drug input:checked") // the list of selected metabolites
      .map((i, element) => {
        return element.value;
      }) // extract the value
      .get() // to a list
      .join("|"),
  };

  tmpl_table = $.templates("#tmpl_table");
  tmpl_row = $.templates("#tmpl_row");
  seen_meta = []; // distinct elements of metabolites
  $("#chart").empty();

  // send request to flask with prop arguments
  $.getJSON("/api?" + $.param(prop), (data) => {
    $("#chart").append(
      tmpl_table.render({ title: toTitleCase(data.query.drug) })
    );

    $.each(data.response.content, (i, row) => {
      title = row[3];
      group = row[7];
      seen = seen_meta.includes(group); // if the selected metabolite has ever been encountered
      if (!seen) seen_meta.push(group); // append the metabolite to the `seen_meta`
      tr_cls = seen ? "" : "tline"; // in [style.css], tr.tline have an attribute `{border-top: 1px solid black;}`
      num_row_in_group = data.response.meta.group_count[group];
      firsttd = seen ? "" : `<td rowspan=${num_row_in_group}>${group}</td>`; // the first column ("Group")

      if (row[14] < 0.001) star = "***";
      else if (row[14] < 0.01) star = "**";
      else if (row[14] < 0.05) star = "*";
      else star = "";

      color = row[12] > 0 ? "rgb(251,180,174)" : "rgb(179,205,227)";

      [
        coef_origin,
        coef_offset,
        error_bar_left,
        error_bar_right,
        error_bar_origin,
      ] = data2svg(
        data.response.meta.minval,
        data.response.meta.maxval,
        row[12],
        row[13]
      );

      $("#chart table tbody").append(
        tmpl_row.render({
          tr_cls: tr_cls,
          firsttd: firsttd,
          title: title,
          star: star,
          coef_origin: coef_origin,
          coef_offset: coef_offset,
          error_bar_left: error_bar_left,
          error_bar_right: error_bar_right,
          error_bar_origin: error_bar_origin,
          color: color,
        })
      );
    });
  });

  $("#spinner").addClass("d-none");
});

// event listner("Select/Deselect All" button)
$("#drug_select_all").click(() => {
  obj = $("#drug_select_all");
  text = obj.text();
  if (text === "Deselect All") {
    $("#meta_drug input").prop("checked", false); // find a tag with #meta_drug and then input tags in it, chaning their "checked" prop.
    obj.text("Select All");
  } else if (text === "Select All") {
    $("#meta_drug input").prop("checked", true);
    obj.text("Deselect All");
  }
});

// event listener("Drug" button)
$("#mode_drug").click(() => {
  // $.views.settings.delimiters("<%", "%>"); // used to edit `.tmpl_table`, `.tmpl_row` tag in [index.html]
  $("#spinner").removeClass("d-none"); // ???

  // make filtering option("Drug" dropwdown)
  $("#wrapper_drug_meta")
    .empty()
    .append(
      `<label class="mb-2">Drug</label>
      <select id="drug_meta" class="form-select mb-4"></select>`
    );
  $.getJSON("/api?mode=list&query=drug", (data) => {
    $.each(data.response, (i, v) => {
      $("#drug_meta").append(`<option value="${v}">${toTitleCase(v)}</option>`);
    });
  });

  // make filtering option("Metabolites" checkboxes)
  $("#drug_select_all").siblings("label").text("Metabolites");
  $("#meta_drug").empty();
  $.getJSON("/api?mode=list&query=meta_group", (data) => {
    $.each(data.response, (i, v) => {
      $("#meta_drug").append(
        `<div class="form-check">
            <input class="form-check-input" type="checkbox" value="${v}" checked>
            <label class="form-check-label">${v}</label>
          </div>`
      );
    });
    $("#spinner").addClass("d-none");
    $("#generate").click(); // sometimes doensn't work.
  });
});

// event listener("Metabolite" button)
$("#mode_meta").click(() => {
  // $.views.settings.delimiters("<%", "%>"); // used to edit `.tmpl_table`, `.tmpl_row` tag in [index.html]
  $("#spinner").removeClass("d-none"); // ???

  // make filtering option(metabolite "Group" dropdown)
  $("#drug_meta").empty().siblings('label').text('Metabolite');
  $.getJSON("/api?mode=list&query=meta", (data) => {
    for (group of Object.keys(data.response)) {
      html = `<optgroup label="${group}">`;
      list_subgroup = data.response[group];
      for (subgroup of list_subgroup) {
        html += `<option value="${subgroup}">${toTitleCase(subgroup)}</option>`;
      }
      $("#drug_meta").append(html);
    }
  });

  // // change the layout of filtering option("Metabolite" dropwdown)
  // $("#wrapper_drug_meta").empty();
  // $("#wrapper_drug_meta").append(
  //   `<div class="row">
  //     <label class="mb-2">Metabolite</label>
  //     <div class="form-group col-sm-6">
  //       <label class="mb-2">Group</label>
  //       <select id="drug_meta" class="form-select mb-4"></select>
  //     </div>
  //     <div class="form-group col-sm-6">
  //       <label class="mb-2">Name</label>
  //       <select id="drug_meta_sub" class="form-select mb-4"></select>
  //     </div>  
  //   </div>`
  // );

  // // make filtering option(metabolite "Group" dropdown)
  // $.getJSON("/api?mode=list&query=meta_group", (data) => {
  //   $.each(data.response, (i, v) => {
  //     $("#drug_meta").append(`<option value="${v}">${toTitleCase(v)}</option>`);
  //   });
  // });

  // // make filtering option(metabolite "Name" dropdown)
  // $.getJSON("/api?mode=list&query=meta_name", (data) => {
  //   $.each(data.response, (i, v) => {
  //     $("#drug_meta_sub").append(
  //       `<option value="${v}">${toTitleCase(v)}</option>`
  //     );
  //   });
  // });

  // make filtering option("Drugs" checkboxes)
  $("#drug_select_all").siblings("label").text("Drugs"); // make 'Metabolites' label to 'Drugs'
  $("#meta_drug").empty();
  $.getJSON("/api?mode=list&query=drug", (data) => {
    $.each(data.response, (i, v) => {
      $("#meta_drug").append(
        `<div class="form-check">
            <input class="form-check-input" type="checkbox" value="${v}" checked>
            <label class="form-check-label">${v}</label>
          </div>`
      );
    });
    $("#spinner").addClass("d-none");
    $("#generate").click(); // sometimes doensn't work.
  });
});

// initialize the ui
init = () => {
  $.views.settings.delimiters("<%", "%>"); // used to edit `.tmpl_table`, `.tmpl_row` tag in [index.html]
  $("#spinner").removeClass("d-none"); // ???

  // make filtering option("Drug" dropwdown)
  $("#drug_meta").empty();
  $.getJSON("/api?mode=list&query=drug", (data) => {
    $.each(data.response, (i, v) => {
      $("#drug_meta").append(`<option value="${v}">${toTitleCase(v)}</option>`);
    });
  });

  // make filtering option("Metabolites" checkboxes)
  $("#meta_drug").empty();
  $.getJSON("/api?mode=list&query=meta_group", (data) => {
    $.each(data.response, (i, v) => {
      $("#meta_drug").append(
        `<div class="form-check">
          <input class="form-check-input" type="checkbox" value="${v}" checked>
          <label class="form-check-label">${v}</label>
        </div>`
      );
    });
    $("#spinner").addClass("d-none");
    $("#generate").click(); // sometimes doensn't work.
  });
};

$(document).ready(init); // when doc(DOM) is ready, start init func.
