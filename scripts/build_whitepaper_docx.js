#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const {
  AlignmentType,
  BorderStyle,
  Document,
  ExternalHyperlink,
  Footer,
  Header,
  HeadingLevel,
  LevelFormat,
  PageBreak,
  PageNumber,
  Packer,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  VerticalAlign,
  WidthType,
} = require("docx");

const project = path.resolve(__dirname, "..");
const input = path.resolve(process.argv[2] || path.join(project, "whitepaper.md"));
const output = path.resolve(process.argv[3] || path.join(project, "whitepaper.docx"));
const source = fs.readFileSync(input, "utf8").replace(/\r\n/g, "\n");
const lines = source.split("\n");

const PAGE_WIDTH = 12240;
const PAGE_HEIGHT = 15840;
const MARGIN = 1080;
const CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN;
const NAVY = "17365D";
const BLUE = "2F75B5";
const PALE_BLUE = "D9EAF7";
const PALE_GRAY = "F2F4F7";
const RULE = "A8B3C2";
const BODY = "202B36";
const MUTED = "5F6B76";

function inlineChildren(text, defaults = {}) {
  const children = [];
  const pattern = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\(https?:\/\/[^)]+\))/g;
  let cursor = 0;
  let match;
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > cursor) {
      children.push(new TextRun({ text: text.slice(cursor, match.index), ...defaults }));
    }
    const token = match[0];
    if (token.startsWith("**")) {
      children.push(
        new TextRun({ text: token.slice(2, -2), bold: true, ...defaults })
      );
    } else if (token.startsWith("*")) {
      children.push(
        new TextRun({ text: token.slice(1, -1), italics: true, ...defaults })
      );
    } else if (token.startsWith("`")) {
      children.push(
        new TextRun({
          text: token.slice(1, -1),
          font: "Courier New",
          color: "334155",
          size: 18,
        })
      );
    } else {
      const link = token.match(/^\[([^\]]+)\]\((https?:\/\/[^)]+)\)$/);
      children.push(
        new ExternalHyperlink({
          link: link[2],
          children: [
            new TextRun({
              text: link[1],
              color: BLUE,
              underline: {},
              ...defaults,
            }),
          ],
        })
      );
    }
    cursor = pattern.lastIndex;
  }
  if (cursor < text.length) {
    children.push(new TextRun({ text: text.slice(cursor), ...defaults }));
  }
  return children.length ? children : [new TextRun({ text: "", ...defaults })];
}

function headingParagraph(text, level) {
  const heading =
    level === 1
      ? HeadingLevel.HEADING_1
      : level === 2
        ? HeadingLevel.HEADING_2
        : HeadingLevel.HEADING_3;
  return new Paragraph({
    heading,
    keepNext: true,
    children: inlineChildren(text),
  });
}

function bodyParagraph(text) {
  return new Paragraph({
    alignment: text.includes("`") ? AlignmentType.LEFT : AlignmentType.JUSTIFIED,
    widowControl: true,
    children: inlineChildren(text),
  });
}

function isDivider(line) {
  return /^---+$/.test(line.trim());
}

function tableWidths(headers) {
  if (headers[0] === "#" && headers.length === 4) {
    return [480, 2450, 4150, 2600];
  }
  if (headers[0] === "Level" && headers.length === 3) {
    return [1650, 5050, 2980];
  }
  if (headers[0] === "Quantity" && headers.length === 3) {
    return [3500, 3090, 3090];
  }
  const raw = headers.map((header) => Math.max(1, Math.min(28, header.length)));
  const total = raw.reduce((sum, value) => sum + value, 0);
  const widths = raw.map((value) => Math.floor((CONTENT_WIDTH * value) / total));
  widths[widths.length - 1] += CONTENT_WIDTH - widths.reduce((a, b) => a + b, 0);
  return widths;
}

function parseTable(start) {
  const rows = [];
  let index = start;
  while (index < lines.length && lines[index].trim().startsWith("|")) {
    const cells = lines[index]
      .trim()
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((cell) => cell.trim());
    if (!cells.every((cell) => /^:?-{3,}:?$/.test(cell))) {
      rows.push(cells);
    }
    index += 1;
  }
  const widths = tableWidths(rows[0]);
  const compact = rows.length > 8;
  const border = { style: BorderStyle.SINGLE, size: 2, color: RULE };
  const borders = { top: border, bottom: border, left: border, right: border };
  const docRows = rows.map(
    (cells, rowIndex) =>
      new TableRow({
        tableHeader: rowIndex === 0,
        cantSplit: true,
        children: cells.map(
          (cell, columnIndex) =>
            new TableCell({
              width: { size: widths[columnIndex], type: WidthType.DXA },
              borders,
              margins: { top: 70, bottom: 70, left: 90, right: 90 },
              verticalAlign: VerticalAlign.CENTER,
              shading: {
                fill:
                  rowIndex === 0
                    ? NAVY
                    : rowIndex % 2 === 0
                      ? PALE_GRAY
                      : "FFFFFF",
                type: ShadingType.CLEAR,
              },
              children: [
                new Paragraph({
                  spacing: { before: 0, after: 0 },
                  children: inlineChildren(cell, {
                    size: compact ? 14 : 16,
                    color: rowIndex === 0 ? "FFFFFF" : BODY,
                    bold: rowIndex === 0,
                  }),
                }),
              ],
            })
        ),
      })
  );
  return {
    next: index,
    element: new Table({
      width: { size: CONTENT_WIDTH, type: WidthType.DXA },
      columnWidths: widths,
      rows: docRows,
    }),
  };
}

const firstTitle = lines.find((line) => line.startsWith("# "));
const firstSubtitle = lines.find((line) => line.startsWith("## "));
const authorLine = lines.find((line) => line.startsWith("**Bobby Morong**"));
const children = [];

children.push(
  new Paragraph({
    spacing: { before: 1500, after: 250 },
    alignment: AlignmentType.LEFT,
    border: {
      top: { style: BorderStyle.SINGLE, size: 26, color: BLUE, space: 1 },
    },
    children: [
      new TextRun({
        text: firstTitle.replace(/^# /, ""),
        font: "Arial",
        size: 54,
        bold: true,
        color: NAVY,
      }),
    ],
  }),
  new Paragraph({
    spacing: { after: 900 },
    children: [
      new TextRun({
        text: firstSubtitle.replace(/^## /, ""),
        font: "Arial",
        size: 28,
        color: BLUE,
      }),
    ],
  }),
  new Paragraph({
    spacing: { after: 160 },
    children: inlineChildren(authorLine.replace(/\*\*/g, ""), {
      size: 21,
      color: BODY,
    }),
  }),
  new Paragraph({
    spacing: { after: 700 },
    children: [
      new TextRun({
        text: "Canonical edition • July 2026",
        size: 19,
        bold: true,
        color: MUTED,
      }),
    ],
  }),
  new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [CONTENT_WIDTH],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: CONTENT_WIDTH, type: WidthType.DXA },
            borders: {
              top: { style: BorderStyle.SINGLE, size: 3, color: BLUE },
              bottom: { style: BorderStyle.SINGLE, size: 3, color: BLUE },
              left: { style: BorderStyle.SINGLE, size: 3, color: BLUE },
              right: { style: BorderStyle.SINGLE, size: 3, color: BLUE },
            },
            margins: { top: 180, bottom: 180, left: 220, right: 220 },
            shading: { fill: PALE_BLUE, type: ShadingType.CLEAR },
            children: [
              new Paragraph({
                spacing: { after: 100 },
                children: [
                  new TextRun({
                    text: "SCIENTIFIC STATUS",
                    bold: true,
                    color: NAVY,
                    size: 18,
                  }),
                ],
              }),
              new Paragraph({
                spacing: { after: 80 },
                children: [
                  new TextRun({
                    text: "A calibrated, LRG2-sensitive 2–3σ hint within published compressed likelihoods. Not a discovery.",
                    bold: true,
                    color: BODY,
                    size: 22,
                  }),
                ],
              }),
              new Paragraph({
                spacing: { after: 0 },
                children: [
                  new TextRun({
                    text: "Includes selection-calibrated influence, direct wCDM-versus-CPL time variation, held-out LRG2 prediction, full-Boltzmann verification, and explicit frontier evidence gates.",
                    color: BODY,
                    size: 18,
                  }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  }),
  new Paragraph({
    spacing: { before: 800, after: 0 },
    children: [
      new TextRun({
        text: "Numerical results frozen at analysis commit 28894e7. Canonical source: whitepaper.md.",
        italics: true,
        color: MUTED,
        size: 17,
      }),
    ],
  }),
  new Paragraph({ children: [new PageBreak()] })
);

let index = lines.findIndex((line) => line.trim() === "## Abstract");
let inNumberedList = false;
for (; index < lines.length; index += 1) {
  const raw = lines[index];
  const line = raw.trim();
  if (!line || isDivider(line)) {
    inNumberedList = false;
    continue;
  }
  if (line.startsWith("|")) {
    const parsed = parseTable(index);
    children.push(parsed.element, new Paragraph({ spacing: { after: 90 } }));
    index = parsed.next - 1;
    inNumberedList = false;
    continue;
  }
  if (line.startsWith("### ")) {
    children.push(headingParagraph(line.slice(4), 2));
    inNumberedList = false;
    continue;
  }
  if (line.startsWith("## ")) {
    children.push(headingParagraph(line.slice(3), 1));
    inNumberedList = false;
    continue;
  }
  if (line.startsWith("#### ")) {
    children.push(headingParagraph(line.slice(5), 3));
    inNumberedList = false;
    continue;
  }
  if (/^- /.test(line)) {
    children.push(
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        children: inlineChildren(line.slice(2)),
      })
    );
    continue;
  }
  const numbered = line.match(/^(\d+)\.\s+(.*)$/);
  if (numbered) {
    children.push(
      new Paragraph({
        numbering: { reference: "references", level: 0 },
        children: inlineChildren(numbered[2]),
      })
    );
    inNumberedList = true;
    continue;
  }
  if (line.startsWith("*") && line.endsWith("*")) {
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: line.replace(/^\*+|\*+$/g, ""),
            italics: true,
            color: MUTED,
            size: 17,
          }),
        ],
      })
    );
    continue;
  }
  children.push(bodyParagraph(line));
}

const doc = new Document({
  creator: "Bobby Morong",
  title: "Anatomy of a 2–3σ Hint",
  subject: "Independent stress test of the DESI DR2 evolving-dark-energy preference",
  description:
    "Canonical July 2026 whitepaper with selection-calibrated influence, direct time-variation calibration, held-out LRG2 diagnostics, and frontier evidence gates.",
  keywords:
    "DESI DR2, dark energy, CPL, LRG2, BAO, cosmology, reproducibility",
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 19, color: BODY },
        paragraph: {
          spacing: { after: 105, line: 276 },
        },
      },
    },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { font: "Arial", size: 30, bold: true, color: NAVY },
        paragraph: {
          spacing: { before: 270, after: 120 },
          outlineLevel: 0,
          keepNext: true,
          border: {
            bottom: { style: BorderStyle.SINGLE, size: 5, color: PALE_BLUE, space: 3 },
          },
        },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { font: "Arial", size: 24, bold: true, color: BLUE },
        paragraph: {
          spacing: { before: 210, after: 90 },
          outlineLevel: 1,
          keepNext: true,
        },
      },
      {
        id: "Heading3",
        name: "Heading 3",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { font: "Arial", size: 21, bold: true, color: BODY },
        paragraph: {
          spacing: { before: 160, after: 70 },
          outlineLevel: 2,
          keepNext: true,
        },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 420, hanging: 220 } } },
          },
        ],
      },
      {
        reference: "references",
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 420, hanging: 260 } } },
          },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
          margin: {
            top: MARGIN,
            right: MARGIN,
            bottom: MARGIN,
            left: MARGIN,
            header: 450,
            footer: 450,
          },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              border: {
                bottom: { style: BorderStyle.SINGLE, size: 3, color: RULE, space: 2 },
              },
              children: [
                new TextRun({
                  text: "DARK-ENERGY STRESS LAB  •  CANONICAL WHITEPAPER",
                  color: MUTED,
                  size: 14,
                  bold: true,
                }),
              ],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              children: [
                new TextRun({ text: "July 2026  •  " , color: MUTED, size: 14 }),
                new TextRun({ children: [PageNumber.CURRENT], color: MUTED, size: 14 }),
              ],
            }),
          ],
        }),
      },
      children,
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(output, buffer);
  process.stdout.write(`wrote ${output}\n`);
});
