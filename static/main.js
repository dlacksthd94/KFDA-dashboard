import { toTitleCase, data2svg } from "./utils.js";

// event listener("Generate" button)
$("#generate").click(() => {
  $("#spinner").removeClass("d-none"); // ???

  // get props from filtering options
  if ($("#mode_drug").prop("checked")) {
    let prop = {
      mode: "drug_chart",
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

    let tmpl_table_header_drug = $.templates("#tmpl_table_header_drug");
    let tmpl_table_row_drug = $.templates("#tmpl_table_row_drug");
    let seen_meta = []; // distinct elements of metabolites

    // send request to flask with prop arguments
    $.getJSON("/api?" + $.param(prop), (data) => {
      $("#chart")
        .empty()
        .append(
          tmpl_table_header_drug.render({ title: toTitleCase(data.query.drug) })
        );

      $.each(data.response.content, (i, row) => {
        let [
          meta_full_name,
          meta_name,
          meta_abb_name,
          meta_group,
          meta_subgroup,
          drug_name,
          cov,
          n,
          beta,
          se,
          p_value,
        ] = row;

        let seen = seen_meta.includes(meta_group); // if the selected metabolite has ever been encountered
        if (!seen) seen_meta.push(meta_group); // append the metabolite to the `seen_meta`
        let tr_cls = seen ? "" : "tline"; // in [style.css], tr.tline have an attribute `{border-top: 1px solid black;}`
        let num_row_in_group = data.response.meta.group_cnt[meta_group];
        let firsttd = seen
          ? ""
          : `<td rowspan=${num_row_in_group}>${meta_group}</td>`; // the first column ("Group")

        let star;
        if (p_value < 0.001) star = "***";
        else if (p_value < 0.01) star = "**";
        else if (p_value < 0.05) star = "*";
        else star = "";

        let color = beta > 0 ? "rgb(251,180,174)" : "rgb(179,205,227)";

        let [
          coef_origin,
          coef_offset,
          error_bar_left,
          error_bar_right,
          error_bar_origin,
        ] = data2svg(
          data.response.meta.minval,
          data.response.meta.maxval,
          beta,
          se
        );

        $("#chart table tbody").append(
          tmpl_table_row_drug.render({
            tr_cls: tr_cls,
            firsttd: firsttd,
            meta_full_name,
            meta_name,
            meta_abb_name,
            meta_group,
            meta_subgroup,
            drug_name,
            cov,
            n,
            beta,
            se,
            p_value,
            star: star,
            coef_origin: coef_origin,
            coef_offset: coef_offset,
            error_bar_left: error_bar_left,
            error_bar_right: error_bar_right,
            error_bar_origin: error_bar_origin,
            color: color,
            i: i,
          })
        );
      });
    });
  } else if ($("#mode_meta").prop("checked")) {
    let prop = {
      mode: "meta_chart",
      meta: $("#drug_meta").val(), // the selected metabolite
      model: $("#drug_model").val(), // the selected model type
      pvalue: $("#drug_pvalue").val(), // the selected p-value type
      drug: $("#meta_drug input:checked") // the list of selected drugs
        .map((i, element) => {
          return element.value;
        }) // extract the value
        .get() // to a list
        .join("|"),
    };

    let tmpl_table_header_meta = $.templates("#tmpl_table_header_meta");
    let tmpl_table_row_meta = $.templates("#tmpl_table_row_meta");

    // $("#chart").empty();

    // send request to flask with prop arguments
    $.getJSON("/api?" + $.param(prop), (data) => {
      $("#chart")
        .empty()
        .append(
          tmpl_table_header_meta.render({ title: toTitleCase(data.query.meta) })
        );

      $.each(data.response.content, (i, row) => {
        let [
          meta_full_name,
          meta_name,
          meta_abb_name,
          meta_group,
          meta_subgroup,
          drug_name,
          cov,
          n,
          beta,
          se,
          p_value,
        ] = row;
        drug_name = drug_name.slice(0, -3);

        let tr_cls = i === 0 ? "tline" : ""; // in [style.css], tr.tline have an attribute `{border-top: 1px solid black;}`

        let star;
        if (p_value < 0.001) star = "***";
        else if (p_value < 0.01) star = "**";
        else if (p_value < 0.05) star = "*";
        else star = "";

        let color = beta > 0 ? "rgb(251,180,174)" : "rgb(179,205,227)";

        let [
          coef_origin,
          coef_offset,
          error_bar_left,
          error_bar_right,
          error_bar_origin,
        ] = data2svg(
          data.response.drug.minval,
          data.response.drug.maxval,
          beta,
          se
        );

        $("#chart table tbody").append(
          tmpl_table_row_meta.render({
            tr_cls: tr_cls,
            meta_full_name,
            meta_name,
            meta_abb_name,
            meta_group,
            meta_subgroup,
            drug_name,
            cov,
            n,
            beta,
            se,
            p_value,
            star: star,
            coef_origin: coef_origin,
            coef_offset: coef_offset,
            error_bar_left: error_bar_left,
            error_bar_right: error_bar_right,
            error_bar_origin: error_bar_origin,
            color: color,
            i: i,
          })
        );
      });
    });
  }

  $("#spinner").addClass("d-none");
});

// event listner("Select/Deselect All" button)
$("#drug_select_all").click(() => {
  let obj = $("#drug_select_all");
  let text = obj.text();
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
  $("#spinner").removeClass("d-none"); // ???

  // make filtering option("Drug" dropwdown)
  $("#wrapper_drug_meta")
    .empty()
    .append(
      `<label class="mb-2">Drug</label>
      <select id="drug_meta" class="form-select mb-4"></select>`
    );
  $.getJSON("/api?mode=sidebar&query=drug", (data) => {
    $.each(data.response, (i, v) => {
      $("#drug_meta").append(`<option value="${v}">${toTitleCase(v)}</option>`);
    });
  });

  // make filtering option("Metabolites" checkboxes)
  $("#drug_select_all").siblings("label").text("Metabolites");
  $("#meta_drug").empty();
  $.getJSON("/api?mode=sidebar&query=meta_group", (data) => {
    $.each(data.response, (i, v) => {
      $("#meta_drug").append(
        `<div class="form-check">
          <label class="form-check-label" for="checkbox${i}" style="cursor:pointer">
          <input class="form-check-input" type="checkbox" value="${v}" id="checkbox${i}" checked style="cursor:pointer">
          ${v}</label>
        </div>`
      );
    });
  });

  $("#spinner").addClass("d-none");
  $("#generate").click(); // sometimes doensn't work.
});

// event listener("Metabolite" button)
$("#mode_meta").click(() => {
  $("#spinner").removeClass("d-none"); // ???

  // make filtering option(metabolite "Group" dropdown)
  $("#drug_meta").empty().siblings("label").text("Metabolite");
  $.getJSON("/api?mode=sidebar&query=meta", (data) => {
    for (let group of Object.keys(data.response)) {
      let html = `<optgroup label="${group}">`;
      let list_subgroup = data.response[group];
      for (let subgroup of list_subgroup) {
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
  // $.getJSON("/api?mode=sidebar&query=meta_group", (data) => {
  //   $.each(data.response, (i, v) => {
  //     $("#drug_meta").append(`<option value="${v}">${toTitleCase(v)}</option>`);
  //   });
  // });

  // // make filtering option(metabolite "Name" dropdown)
  // $.getJSON("/api?mode=sidebar&query=meta_name", (data) => {
  //   $.each(data.response, (i, v) => {
  //     $("#drug_meta_sub").append(
  //       `<option value="${v}">${toTitleCase(v)}</option>`
  //     );
  //   });
  // });

  // make filtering option("Drugs" checkboxes)
  $("#drug_select_all").siblings("label").text("Drugs"); // make 'Metabolites' label to 'Drugs'
  $("#meta_drug").empty();
  $.getJSON("/api?mode=sidebar&query=drug", (data) => {
    $.each(data.response, (i, v) => {
      $("#meta_drug").append(
        `<div class="form-check">
          <label class="form-check-label" for="checkbox${i}" style="cursor:pointer">
          <input class="form-check-input" type="checkbox" value="${v}" id="checkbox${i}" checked style="cursor:pointer">
          ${v}</label>
        </div>`
      );
    });
  });

  $("#spinner").addClass("d-none");
  $("#generate").click(); // sometimes doensn't work.
});

// make filtering option(metabolite "Name" in the table)
$(document).on("click", '#meta_name', function (x) {
  let meta = x.currentTarget.textContent;

  $("#mode_meta").click();
  
  // make filtering option(metabolite "Group" dropdown)
  $("#drug_meta").empty().siblings("label").text("Metabolite");
  $.getJSON("/api?mode=sidebar&query=meta", (data) => {
    for (let group of Object.keys(data.response)) {
      let html = `<optgroup label="${group}">`;
      let list_subgroup = data.response[group];
      for (let subgroup of list_subgroup) {
        if (subgroup == meta) {
          html += `<option value="${subgroup}" selected>${toTitleCase(subgroup)}</option>`;
        } else {
          html += `<option value="${subgroup}">${toTitleCase(subgroup)}</option>`;
        }        
      }
      $("#drug_meta").append(html);
    }
  });

  // make filtering option("Drugs" checkboxes)
  $("#drug_select_all").siblings("label").text("Drugs"); // make 'Metabolites' label to 'Drugs'
  $("#meta_drug").empty();
  $.getJSON("/api?mode=sidebar&query=drug", (data) => {
    $.each(data.response, (i, v) => {
      $("#meta_drug").append(
        `<div class="form-check">
          <label class="form-check-label" for="checkbox${i}" style="cursor:pointer">
          <input class="form-check-input" type="checkbox" value="${v}" id="checkbox${i}" checked style="cursor:pointer">
          ${v}</label>
        </div>`
      );
    });
  });

  setTimeout(() => {$("#generate").click()}, 500)
});

// make filtering option(drug "Name" in the table)
$(document).on("click", '#drug_name', function (x) {
  let drug = x.currentTarget.textContent;
  
  $("#mode_drug").click();

  // make filtering option("Drug" dropwdown)
  $("#wrapper_drug_meta")
    .empty()
    .append(
      `<label class="mb-2">Drug</label>
      <select id="drug_meta" class="form-select mb-4"></select>`
    );
  $.getJSON("/api?mode=sidebar&query=drug", (data) => {
    $.each(data.response, (i, v) => {
      if (v == drug) {
        $("#drug_meta").append(`<option value="${v}" selected>${toTitleCase(v)}</option>`);
      } else {
        $("#drug_meta").append(`<option value="${v}">${toTitleCase(v)}</option>`);
      }
      
    });
  });

  // make filtering option("Metabolites" checkboxes)
  $("#drug_select_all").siblings("label").text("Metabolites");
  $("#meta_drug").empty();
  $.getJSON("/api?mode=sidebar&query=meta_group", (data) => {
    $.each(data.response, (i, v) => {
      $("#meta_drug").append(
        `<div class="form-check">
          <label class="form-check-label" for="checkbox${i}" style="cursor:pointer">
          <input class="form-check-input" type="checkbox" value="${v}" id="checkbox${i}" checked style="cursor:pointer">
          ${v}</label>
        </div>`
      );
    });
  });

  setTimeout(() => {$("#generate").click()}, 500)
});

// initialize the ui
const init = () => {
  $.views.settings.delimiters("<%", "%>"); // used to edit templates in [index.html]
  $("#spinner").removeClass("d-none"); // ???

  // make filtering option("Drug" dropwdown)
  $("#drug_meta").empty();
  $.getJSON("/api?mode=sidebar&query=drug", (data) => {
    $.each(data.response, (i, v) => {
      $("#drug_meta").append(`<option value="${v}">${toTitleCase(v)}</option>`);
    });
  });

  // make filtering option("Metabolites" checkboxes)
  $("#meta_drug").empty();
  $.getJSON("/api?mode=sidebar&query=meta_group", (data) => {
    $.each(data.response, (i, v) => {
      $("#meta_drug").append(
        `<div class="form-check">
          <label class="form-check-label" for="checkbox${i}" style="cursor:pointer">
          <input class="form-check-input" type="checkbox" value="${v}" id="checkbox${i}" checked style="cursor:pointer">
          ${v}</label>
        </div>`
      );
    });
    $("#spinner").addClass("d-none");
    setTimeout(() => {$("#generate").click()}, 50)
    // $("#generate").click(); // sometimes doensn't work.
  });
};

$(document).ready(init); // when doc(DOM) is ready, start init func.
