import "./index.scss";

document.addEventListener("DOMContentLoaded", function () {
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

  function openSocket() {
    $logger.children[1].disabled = true;
    const schema = window.location.protocol === "http:" ? "ws://" : "wss://";
    const wsURL =
      schema +
      (process.env.NODE_ENV === "production"
        ? "dadescomunals.org/hemeroteca-oberta/ws"
        : "localhost:8000/ws");

    const ws = new WebSocket(wsURL);

    ws.onmessage = function (event) {
      const data = JSON.parse(event.data);
      if (data.type === "info") {
        if (data.body.total === 0) {
          $logger.children[0].innerHTML = "No s'han trobat coincidències";
          ws.close();
        } else {
          $logger.children[0].innerHTML = `Descarregant resultats coincidents amb la paraula '${data.body.word}<br/><strong>Pàgina ${data.body.page} de ${data.body.total}`;
          ws.send(
            JSON.stringify({ type: "response", body: { status: "sync" } })
          );
        }
      } else if (data.type === "event") {
        if (data.body.event === "closed") {
          const schema = window.location.protocol;
          const fileURL =
            process.env.NODE_ENV === "production"
              ? schema +
                "//dadescomunals.org/hemeroteca-oberta/file/" +
                data.body.fileId
              : schema + "//localhost:8000/file/" + data.body.fileId;
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

    ws.onclose = function (ev) {
      $submit.disabled = true;
    };

    return new Promise((done, error) => {
      ws.onopen = function (ev) {
        done(ws);
      };

      ws.onerror = function (ev) {
        console.warn(ev);
        try {
          ws.close();
        } catch (err) {}
      };
    });

    return ws;
  }

  $inputs.forEach(function ($input) {
    $input.addEventListener("input", function () {
      let name = $input.getAttribute("name");
      let value = $input.value;
      // if (name === "word") value = value.replace(/\s+/, "+");
      // value = encodeURIComponent(value);
      query[name] = value;
      $submit.disabled = !isQueryReady();
    });
  });

  $submit.addEventListener("click", function (ev) {
    ev.preventDefault();

    if ($submit.disabled) return;

    if (isQueryReady() === false) return;

    openSocket().then(ws => {
      ws.send(
        JSON.stringify({
          type: "query",
          ...query
        })
      );
    });
  });
});
