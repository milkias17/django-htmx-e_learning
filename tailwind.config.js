const path = require("path");
const projectRoot = path.resolve(__dirname);

const { spawnSync } = require("child_process");

/**
 * @type {string[] | null}
 */
let cachedTemplateFiles = null;

function getTemplateFiles() {
  if (cachedTemplateFiles) return cachedTemplateFiles;
  console.log("Getting template files from django....")

  const command = "python"; // Requires virtualenv to be activated.
  const args = ["manage.py", "list_templates"]; // Requires cwd to be set.
  const options = { cwd: projectRoot };
  const result = spawnSync(command, args, options);

  if (result.error) {
    throw result.error;
  }

  if (result.status !== 0) {
    console.log(result.stdout.toString(), result.stderr.toString());
    throw new Error(
      `Django management command exited with code ${result.status}`,
    );
  }

  const templateFiles = result.stdout
    .toString()
    .split("\n")
    .map((file) => file.trim())
    .filter(function (e) {
      return e;
    }); // Remove empty strings, including last empty line.
  cachedTemplateFiles = templateFiles;
  return templateFiles;
};

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/forms.py"].concat(getTemplateFiles()),
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  daisyui: {
    themes: ["emerald", "corporate", "light", "dark", "cupcake", "halloween", "aqua"],
  },
  safelist: [
    "mask-half-1",
    "mask-half-2",
    "alert-info",
    "alert-success",
    "alert-warning",
    "alert-error",
  ],
};
