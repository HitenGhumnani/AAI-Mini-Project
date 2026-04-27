import "./style.css";

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
  <main class="container">
    <h1>Pix2Pix Image Translation</h1>
    <p class="subtitle">Upload a blueprint/label image and generate a facade.</p>

    <form id="upload-form" class="card">
      <label for="image-input">Input image</label>
      <input id="image-input" type="file" accept="image/*" required />
      <button id="generate-btn" type="submit">Generate Output</button>
      <p id="status" class="status">Choose an image to begin.</p>
    </form>

    <section class="preview-grid">
      <article class="preview-card">
        <h2>Input Preview</h2>
        <img id="input-preview" alt="Selected input preview" />
      </article>
      <article class="preview-card">
        <h2>Generated Output</h2>
        <img id="output-preview" alt="Generated output preview" />
      </article>
    </section>
  </main>
`;

const form = document.querySelector<HTMLFormElement>("#upload-form")!;
const input = document.querySelector<HTMLInputElement>("#image-input")!;
const statusText = document.querySelector<HTMLParagraphElement>("#status")!;
const inputPreview = document.querySelector<HTMLImageElement>("#input-preview")!;
const outputPreview = document.querySelector<HTMLImageElement>("#output-preview")!;
const generateBtn = document.querySelector<HTMLButtonElement>("#generate-btn")!;

input.addEventListener("change", () => {
  const file = input.files?.[0];
  if (!file) return;
  inputPreview.src = URL.createObjectURL(file);
  outputPreview.removeAttribute("src");
  statusText.textContent = "Image selected. Click Generate Output.";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = input.files?.[0];
  if (!file) {
    statusText.textContent = "Please choose an image first.";
    return;
  }

  const formData = new FormData();
  formData.append("image", file);

  try {
    statusText.textContent = "Generating...";
    generateBtn.disabled = true;

    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const blob = await response.blob();
    outputPreview.src = URL.createObjectURL(blob);
    statusText.textContent = "Done! Output image generated.";
  } catch (error) {
    console.error(error);
    statusText.textContent = "Prediction failed. Check backend logs.";
  } finally {
    generateBtn.disabled = false;
  }
});
