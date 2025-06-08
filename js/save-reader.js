function updatePokemonSprites(speciesNames) {
    const monSlots = document.querySelectorAll(".pokemon-slot");
    const monBox = document.getElementById("box-list");
    speciesNames.forEach((name, index) => {
        if (index < 6) {
              monSlots[index].src = `https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${name}.png`;
        }
        else {
            const img = document.createElement("img");
            img.src = `https://raw.githubusercontent.com/PurpleYoyo/LittleEmerald-SaveReader/main/sprites/${name}.png`;
            img.className = "pokemon-slot";
            img.alt = `${name}`;
            monBox.appendChild(img);
        }
      });
}

async function readSave() {
    document.getElementById("spinner").style.display = "inline-block";
    const btn = document.getElementById("load-save");
    btn.disabled = true;
    btn.textContent = "Parsing…";

    let fileInput = document.getElementById("fileInput");
        if (!fileInput.files.length) {
                alert("Please select a file first.");
                document.getElementById("spinner").style.display = "none";
                btn.disabled = false;
                  btn.textContent = "Load";
                return;
        }
    let file = fileInput.files[0];
    let reader = new FileReader();

    reader.onload = async function (event) {
        let arrayBuffer = event.target.result;
    
         let pyodide = await loadPyodide();
        await pyodide.loadPackage("pyodide-http")
    
        let response = await fetch("https://PurpleYoyo.github.io/LittleEmerald-SaveReader/read.py");
        let code = await response.text();

        await pyodide.runPythonAsync(code);

        let uint8Array = new Uint8Array(arrayBuffer);
        let saveDataPy = `bytes([${uint8Array.join(",")}])`;
        
        let evsEnabled = document.getElementById("evs").checked;
          pyodide.globals.set("evs", evsEnabled);

        let debug = document.getElementById("debug").checked;
        pyodide.globals.set("debug", debug);

        let output = await pyodide.runPythonAsync(`read(${saveDataPy}, evs=evs, debug=debug)`);
        let [import_data, species_names] = output.toJs();
        document.getElementById("output").textContent = import_data;

        if (document.getElementById("sprites").checked)
            updatePokemonSprites(species_names);

        document.getElementById("spinner").style.display = "none";
        btn.disabled = false;
          btn.textContent = "Load";
    };
    reader.readAsArrayBuffer(file);
}