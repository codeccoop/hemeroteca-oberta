document.addEventListener("DOMContentLoaded", function () {
  var $app = document.getElementById("app");
  var $form = $app.getElementsByClassName("app__form")[0];
  var $inputs = Array.apply(null, $form.getElementsByClassName("app__input"));
  var $submit = $form.getElementsByClassName("app__button")[0];
  var $status = $app.getElementsByClassName("app__status")[0];

  var query = {
    word: null,
    start_date: null,
    end_date: null,
  };

  function isQueryReady() {
    return Object.keys(query).reduce((ready, field) => {
      return ready && query[field] !== null;
    }, true);
  }

  $inputs.forEach(function ($input) {
    $input.addEventListener("input", function () {
      query[$input.getAttribute("name")] = $input.value;
      if (isQueryReady() === true) $submit.disabled = false;
    });
  });

  $submit.addEventListener("click", function (ev) {
    ev.preventDefault();

    if ($submit.disabled) return;

    if (isQueryReady() === false) return;

    ws.send(
      JSON.stringify({
        type: "query",
        ...query,
      })
    );
  });

  const ws = new WebSocket(`ws://${window._env.domain}/${window._env.baseurl}/ws`);
  ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.type === "info") {
      $status.innerHTML = `Descarregant resultats coincidents amb la paraula '${data.body.word}<br/><strong>Pàgina ${data.body.page} de ${data.body.total}`;
    } else if (data.type === "event") {
      if (data.body.event === "closed") {
        fetch(window._env.baseurl + "/file/" + data.body.fileId)
          .then(res => res.blob())
          .then(blob => {
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = url;
            a.download = data.body.fileId + ".csv";
            document.body.appendChild(a);
            a.click();
            a.remove();
          });
      }
    }
    ws.send(JSON.stringify({ type: "response", body: { "status": "sync" } }));
  };
});
