import "./index.scss";

document.addEventListener("DOMContentLoaded", function () {
  debugger;
  var $app = document.getElementsByClassName("app")[0];
  var $form = $app.getElementsByClassName("form")[0];
  var $inputs = Array.apply(
    null,
    $form.getElementsByClassName("form__field")
  ).map(field => field.children[1]);
  var $submit = $form.getElementsByClassName("form__button")[0];
  var $logger = $app.getElementsByClassName("logger")[0];

  var query = {
    word: null,
    start_date: null,
    end_date: null
  };

  function isQueryReady() {
    return Object.keys(query).reduce((ready, field) => {
      return ready && query[field] !== null && query[field] !== "";
    }, true);
  }

  $inputs.forEach(function ($input) {
    $input.addEventListener("input", function () {
      query[$input.getAttribute("name")] = $input.value;
      $submit.disabled = !isQueryReady();
    });
  });

  $submit.addEventListener("click", function (ev) {
    ev.preventDefault();

    if ($submit.disabled) return;

    if (isQueryReady() === false) return;

    ws.send(
      JSON.stringify({
        type: "query",
        ...query
      })
    );
  });

  const wsURL =
    process.env.NODE_ENV === "production"
      ? "wss://dadescomunals.org/hemeroteca-oberta/ws"
      : "ws://localhost:8000/ws";

  const ws = new WebSocket(wsURL);
  ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.type === "info") {
      $logger.children[0].innerHTML = `Descarregant resultats coincidents amb la paraula '${data.body.word}<br/><strong>Pàgina ${data.body.page} de ${data.body.total}`;

      ws.send(JSON.stringify({ type: "response", body: { status: "sync" } }));
    } else if (data.type === "event") {
      if (data.body.event === "closed") {
        const fileURL =
          process.env.NODE_ENV === "production"
            ? "https://dadescomunals.org/hemeroteca-oberta/file/" +
              data.body.fileId
            : "http://localhost:8000/file/" + data.body.fileId;
        fetch(fileURL)
          .then(res => res.blob())
          .then(blob => {
            $logger.children[1].disabled = false;
            $logger.children[1].addEventListener("click", function () {
              var url = window.URL.createObjectURL(blob);
              var a = document.createElement("a");
              a.href = url;
              a.download = data.body.fileId + ".csv";
              document.body.appendChild(a);
              a.click();
              a.remove();
              $logger.children[1].disabled = true;
            });
          });
      }
    }
  };
});
