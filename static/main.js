// functions
toTitleCase = (s) => s.replace(/\w\S*/g, (t) => t.charAt(0).toUpperCase() + t.substr(1));

data2svg = (minval, maxval, coef, se) => {
  conv = (x) => 500 * (x - minval) / (maxval - minval);
  if (coef > 0) {
    return [conv(0), conv(coef) - conv(0), 'rgb(251,180,174)', conv(coef - 1.96 * se), conv(coef + 1.96 * se), conv(coef)];
  } else {
    return [conv(coef), conv(0) - conv(coef), 'rgb(179,205,227)', conv(coef - 1.96 * se), conv(coef + 1.96 * se), conv(coef)];
  }
};

// ui event listeners
$('#generate').click(() => {
  $('#spinner').removeClass('d-none');
  if ($('#mode_drug').prop('checked')) m = 'drug';
  else if ($('#mode_meta').prop('checked')) m = 'meta';
  p = {
    m: m + '_chart',
    drug: $('#drug_drug').val(),
    model: $('#drug_model').val(),
    pvalue: $('#drug_pvalue').val(),
    bioms: [],
  };
  $('#drug_bioms input:checked').each((idx, elm) => {
    obj = $(elm);
    p.bioms.push(obj.val());
  });
  p.bioms = p.bioms.join('|');
  console.log($.param(p));
  tmpl_table = $.templates('#tmpl_table');
  tmpl_row = $.templates('#tmpl_row');
  seen_bioms = [];
  $('#chart').empty();
  $.getJSON('/api?' + $.param(p), (data) => {
    console.log(data);
    $('#chart').append(tmpl_table.render({ title: toTitleCase(data.query.drug) }));
    $.each(data.response.content, (i, r) => {
      seen = seen_bioms.includes(r[7]);
      if (!seen) seen_bioms.push(r[7]);
      trcls = seen ? '' : 'tline';
      firsttd = seen ? '' : '<td rowspan=' + data.response.meta.group_count[r[7]] + '>' + r[7] + '</td>';
      subg = r[2];
      if (r[14] < .001) star = '***';
      else if (r[14] < .01) star = '**';
      else if (r[14] < .05) star = '*';
      else star = '';
      color = r[12] > 0 ? 'rgb(251,180,174)' : 'rgb(179,205,227)';
      [rectx, rectw, color, linex1, linex2, circlex] = data2svg(data.response.meta.minval, data.response.meta.maxval, r[12], r[13]);
      console.log([trcls, firsttd, subg, star, rectx, rectw, color, linex1, linex2, circlex]);
      $('#chart table tbody').append(tmpl_row.render({ trcls: trcls, firsttd: firsttd, subg: subg, star: star, rectx: rectx, rectw: rectw, color: color, linex1: linex1, linex2: linex2, circlex: circlex }));
    });
  });
  $('#spinner').addClass('d-none');
});

$('#drug_select_all').click(() => {
  obj = $('#drug_select_all');
  t = obj.text();
  if (t === 'Deselect All') {
    $('#drug_bioms input').prop('checked', false);
    obj.text('Select All');
  } else if (t === 'Select All') {
    $('#drug_bioms input').prop('checked', true);
    obj.text('Deselect All');
  }
});

// initialize the ui
init = () => {
  $.views.settings.delimiters('<%', '%>');
  $('#spinner').removeClass('d-none');
  $('#drug_drug').empty();
  $.getJSON('/api?m=list&q=drug', (data) => {
    $.each(data.response, (i, v) => {
      $('#drug_drug').append('<option value="' + v + '">' + toTitleCase(v) + '</option>');
    });
  });
  $('#drug_bioms').empty();
  $.getJSON('/api?m=list&q=biom', (data) => {
    $.each(data.response, (i, v) => {
      $('#drug_bioms').append('<div class="form-check"><input class="form-check-input" type="checkbox" value="' + v + '" checked><label class="form-check-label">' + v + '</label></div>');
    });
    $('#spinner').addClass('d-none');
    $('#generate').click();
  });
}

$(document).ready(init);

