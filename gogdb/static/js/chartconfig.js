function null_to_nan(value)
{
  if (value == null) {
    return NaN;
  }
  return value;
}

chart_init_called = false;
function init_chart()
{
  if (chart_init_called) {
      console.log("Chart already initialized");
      return;
  }
  chart_init_called = true;

  var discount= JSON.parse(document.getElementById("discount-json").innerHTML)
  discount["values"] = discount["values"].map(null_to_nan);

  var config = {
    type: "line",
    data: {
      labels: discount["labels"],
      datasets: [{
        label: "Discount",
        fill: false,
        steppedLine: true,
        borderColor: "rgb(241, 142, 0)",
        backgroundColor: "rgb(241, 142, 0)",
        data: discount["values"],
      }]
    },
    options: {
      title: {
        display: true,
        text: 'Discount Records'
      },
      scales: {
        xAxes: [{
          type: "time",
          time: {
            tooltipFormat: "MMM D, YYYY",
          }
        }],
        yAxes: [{
          ticks: {
              min: 0,
              max: 100,
              reverse: true
          }
        }]
      },
      legend: {
        display: false
      },
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: 15
        }
      }
    }
  };

  var ctx = document.getElementById("chart-canvas");
  if (ctx != null) {
    window.myChart = new Chart(ctx, config);
  }
};

window.addEventListener("DOMContentLoaded", init_chart, false);
