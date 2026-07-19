export type ToolGuideFaq = {
  question: string;
  answer: string;
};

export type ToolGuide = {
  whatIs: string;
  howTo: string[];
  benefits: string[];
  useCases: string[];
  example: string;
  faqs: ToolGuideFaq[];
  updatedAt: string;
};

const UPDATED_AT = "2026-07-18";

export const TOOL_GUIDES: Record<string, ToolGuide> = {
  "json-formatter": {
    whatIs: `A JSON formatter turns raw, hard-to-read JavaScript Object Notation into a clean, indented structure you can scan in seconds. Developers paste API responses, config files, or log payloads into the ToolVerse JSON Formatter at tool-verse.online and immediately see nested objects, arrays, and keys lined up with consistent spacing.

Beyond pretty-printing, a solid formatter also validates syntax: missing commas, trailing commas in strict mode, unquoted keys, and mismatched braces surface as clear errors instead of silent failures later in production. That feedback loop is why teams keep a formatter open beside their editor when debugging webhooks, GraphQL payloads, or exported analytics dumps.

The ToolVerse version runs in your browser whenever possible, so sensitive tokens and customer records do not need to leave your machine for a quick cleanup. You get readable JSON, validation, and a copy-ready result without installing a desktop app.`,
    howTo: [
      "Open the JSON Formatter on ToolVerse and paste your raw JSON into the input panel.",
      "Click Format (or Beautify) to indent nested structures and normalize whitespace.",
      "If an error appears, fix the highlighted syntax issue and format again until validation passes.",
      "Optionally minify the same payload when you need a compact single-line string for storage or transport.",
      "Copy the output and paste it into your editor, ticket, or API client.",
      "Save frequently used samples in your local history if you are signed in, so you can revisit them later.",
    ],
    benefits: [
      "Catch malformed JSON before it breaks a deploy or integration test.",
      "Compare nested API responses visually without squinting at minified blobs.",
      "Share readable payloads in pull requests and incident write-ups.",
      "Switch between pretty and compact forms for docs versus wire size.",
      "Work quickly in the browser without installing IDE plugins for every machine.",
    ],
    useCases: [
      "Debugging REST or webhook responses that arrive as a single compressed line.",
      "Cleaning exported Firebase, Stripe, or analytics JSON before analysis.",
      "Preparing example payloads for API documentation and onboarding guides.",
      "Validating hand-edited configuration files before committing them.",
      "Teaching juniors how object nesting and arrays map to real data.",
    ],
    example: `Input (minified):
{"user":{"id":42,"roles":["admin","editor"],"meta":{"active":true}}}

Formatted output:
{
  "user": {
    "id": 42,
    "roles": [
      "admin",
      "editor"
    ],
    "meta": {
      "active": true
    }
  }
}

Tip: if Format fails with "Unexpected token", check for a trailing comma after the last property—common when copying from JavaScript object literals.`,
    faqs: [
      {
        question: "Does the ToolVerse JSON Formatter send my data to a server?",
        answer:
          "Formatting and validation run in the browser for typical payloads, so your content stays on your device. Avoid pasting secrets into any online tool if your policy forbids it; use local tooling for regulated data.",
      },
      {
        question: "Can it fix invalid JSON automatically?",
        answer:
          "It highlights syntax problems so you can correct them. It does not silently invent missing quotes or keys, because that could change meaning. Fix the error, then format again.",
      },
      {
        question: "What is the difference between format and minify?",
        answer:
          "Format adds indentation and line breaks for humans. Minify removes unnecessary whitespace so the same structure takes less space in logs, caches, or query strings.",
      },
      {
        question: "Does it support JSON5 or comments?",
        answer:
          "Standard JSON does not allow comments. If your source includes // or /* */ comments, strip them or convert to strict JSON before formatting.",
      },
      {
        question: "Why does my number look different after formatting?",
        answer:
          "Formatting should not change numeric values. If a value appears altered, you may have pasted a non-JSON type (BigInt, undefined) or a string that only looked like a number.",
      },
    ],
    updatedAt: UPDATED_AT,
  },

  base64: {
    whatIs: `Base64 encoding converts binary data into a safe ASCII string using 64 printable characters. It is not encryption—anyone can decode it—but it is essential whenever you must embed bytes inside text-only channels: JSON fields, HTML data URLs, email MIME parts, or configuration files that reject raw binary.

Developers use Base64 constantly when shipping small images as data URIs, encoding API credentials for Basic Auth headers, or moving file contents through clipboard-friendly text. The ToolVerse Base64 tool at tool-verse.online lets you encode text or decode strings back to readable output without writing a one-off script.

Understanding Base64 also helps you spot mistakes: padding with = characters, URL-safe variants that replace + and /, and the roughly 33% size increase after encoding. Having a reliable encoder/decoder nearby keeps those details from slowing you down during integrations.`,
    howTo: [
      "Open the Base64 tool on ToolVerse and choose Encode or Decode.",
      "Paste plain text (or a Base64 string) into the input area.",
      "Run the conversion and review the output for expected length and padding.",
      "Copy the result into your header, config file, or data URL.",
      "For URL-safe contexts, verify whether your target system expects +/ or -_ alphabets.",
      "Double-check that you are not treating Base64 as a security control—use real encryption when secrecy matters.",
    ],
    benefits: [
      "Move binary-friendly payloads through text-only APIs and logs.",
      "Build or inspect data URLs for small icons and inline assets.",
      "Debug Basic Auth and other Base64-wrapped headers quickly.",
      "Avoid writing throwaway encode scripts in every language you touch.",
      "Learn padding and alphabet quirks with immediate visual feedback.",
    ],
    useCases: [
      "Encoding a short SVG or PNG for an HTML data URI.",
      "Decoding a JWT payload segment after splitting on periods (with care for URL-safe Base64).",
      "Preparing client_id:client_secret pairs for HTTP Basic Authentication.",
      "Inspecting email attachments or MIME parts represented as Base64.",
      "Converting clipboard text that arrived as an opaque encoded blob.",
    ],
    example: `Encode text:
Hello ToolVerse → SGVsbG8gVG9vbFZlcnNl

Decode:
SGVsbG8gVG9vbFZlcnNl → Hello ToolVerse

Data URL sketch:
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...

Note: decoding random strings may produce binary garbage. If the result looks wrong, confirm the alphabet (standard vs URL-safe) and padding.`,
    faqs: [
      {
        question: "Is Base64 encryption?",
        answer:
          "No. Base64 is an encoding scheme. It obscures bytes only in the sense that they are no longer readable as plain text, but it is trivial to reverse. Use HTTPS and proper cryptography for confidentiality.",
      },
      {
        question: "Why does my encoded string end with = or ==?",
        answer:
          "Padding characters fill the last block so the length is a multiple of four. Some systems strip padding; others require it. Match the expectation of the API you call.",
      },
      {
        question: "What is URL-safe Base64?",
        answer:
          "A variant that replaces + with - and / with _ so the string survives in URLs and filenames without extra escaping. JWTs commonly use this form.",
      },
      {
        question: "Can I encode entire files?",
        answer:
          "Yes for small files, but remember the ~33% size increase. Large binaries are better uploaded as multipart or stored as blobs rather than embedded as Base64 in JSON.",
      },
      {
        question: "Why does decode fail with an invalid character error?",
        answer:
          "The input likely includes whitespace, line breaks, or characters outside the Base64 alphabet. Strip formatting and confirm you did not mix URL-safe and standard alphabets.",
      },
    ],
    updatedAt: UPDATED_AT,
  },

  "color-converter": {
    whatIs: `A color converter translates between color models—HEX, RGB, HSL, and related notations—so designers and developers stay aligned across Figma, CSS, and design tokens. What looks like #0EA5E9 in a brand guide becomes rgb(14, 165, 233) or hsl(199 89% 48%) depending on the toolchain you are in.

Manual conversion is error-prone: a swapped channel or missing leading zero can ship the wrong accent on production. The ToolVerse Color Converter at tool-verse.online gives instant, bidirectional conversion so you can paste any common format and copy the one your stylesheet or token file expects.

Accurate conversion also supports accessibility work. When you adjust lightness in HSL and re-export HEX, you can iterate toward contrast targets without guessing. Pair the converter with your contrast checker and you move faster from brand color to usable UI states.`,
    howTo: [
      "Open the Color Converter and paste a HEX, RGB, or HSL value into the input.",
      "Review the converted outputs shown for each supported format.",
      "Copy the format required by your CSS, design token, or design tool.",
      "Tweak HSL lightness or saturation if you are exploring variants, then reconvert.",
      "Verify the result against a live preview or your design system sample.",
      "Document the chosen token so the team stops hard-coding one-off HEX values.",
    ],
    benefits: [
      "Eliminate hand-conversion mistakes between design and engineering.",
      "Explore tints and shades via HSL while keeping HEX for tokens.",
      "Speed up theme migration when moving from RGB to modern CSS color spaces.",
      "Keep brand colors consistent across marketing pages and product UI.",
      "Support accessibility iterations with predictable channel adjustments.",
    ],
    useCases: [
      "Turning a Figma HEX swatch into CSS custom properties.",
      "Building dark-mode variants by adjusting HSL lightness systematically.",
      "Matching an accent color from a screenshot approximated as RGB.",
      "Migrating legacy rgb() declarations into HEX tokens for a design system.",
      "Preparing color tables for email templates that prefer HEX.",
    ],
    example: `Input HEX: #0EA5E9

RGB: rgb(14, 165, 233)
HSL: hsl(199, 89%, 48%)

CSS token suggestion:
--accent: #0EA5E9;
--accent-rgb: 14 165 233;

For a softer hover state, raise lightness in HSL (for example to ~55%) and convert back to HEX before updating your theme.`,
    faqs: [
      {
        question: "Does the converter support 8-digit HEX with alpha?",
        answer:
          "Many converters accept #RRGGBBAA or separate opacity fields. If you need transparency in CSS, prefer modern formats like rgb(14 165 233 / 0.8) after converting the opaque base color.",
      },
      {
        question: "Why do two HEX values look the same but convert differently?",
        answer:
          "Displays and color profiles can make nearby colors appear identical. Trust the numeric channels when implementing tokens, and verify contrast with a dedicated checker.",
      },
      {
        question: "Should I store colors as HEX or HSL in a design system?",
        answer:
          "HEX (or OKLCH in modern systems) is common for final tokens. HSL is useful while editing. Store the canonical value your platform renders most reliably, and generate other formats as needed.",
      },
      {
        question: "Can I convert named CSS colors like tomato?",
        answer:
          "If the tool accepts named colors, it maps them to their defined RGB values. Otherwise, look up the named color once, then convert from HEX/RGB going forward.",
      },
      {
        question: "Is HSL the same as HSV?",
        answer:
          "No. HSL and HSV arrange lightness/value differently, so the same hue and saturation numbers are not interchangeable. Convert carefully if your design tool uses HSV.",
      },
    ],
    updatedAt: UPDATED_AT,
  },

  "hash-generator": {
    whatIs: `A hash generator computes a fixed-length digest from any input using algorithms such as MD5, SHA-1, SHA-256, or SHA-512. Hashes are one-way: you cannot reconstruct the original text from the digest, which makes them useful for integrity checks, cache keys, and fingerprinting content.

Security-sensitive uses demand care. MD5 and SHA-1 are broken for collision resistance and should not protect passwords or certificates. Prefer SHA-256 (or stronger) for integrity, and dedicated password hashing (bcrypt, Argon2, scrypt) for credentials. The ToolVerse Hash Generator at tool-verse.online helps you compute digests quickly while you decide which algorithm fits the job.

Teams also use hashes in build pipelines: content-addressable storage, ETag generation, and verifying that a downloaded artifact matches a published checksum. A browser-side generator is ideal for ad-hoc checks without installing OpenSSL on every laptop.`,
    howTo: [
      "Open the Hash Generator and paste or type the text you want to fingerprint.",
      "Select an algorithm appropriate for your use case (prefer SHA-256 for integrity).",
      "Generate the digest and copy the hexadecimal output.",
      "Compare it against a published checksum or store it alongside the artifact.",
      "If hashing files, confirm whether the tool hashes raw bytes or a text interpretation of the content.",
      "Never use a fast general-purpose hash alone to store user passwords.",
    ],
    benefits: [
      "Verify downloads and releases against published checksums.",
      "Create stable cache keys from normalized request bodies.",
      "Detect accidental content changes between environments.",
      "Prototype integrity flows before wiring server-side crypto libraries.",
      "Compare algorithm outputs side by side while learning cryptography basics.",
    ],
    useCases: [
      "Confirming a Linux ISO or npm package matches its SHA-256 sum.",
      "Generating deterministic IDs for deduplicating uploaded documents.",
      "Building weak ETags during API prototyping (upgrade for production needs).",
      "Teaching the difference between hashing and encryption in workshops.",
      "Fingerprinting canonical JSON after sorting keys for webhook verification sketches.",
    ],
    example: `Input text:
tool-verse.online

SHA-256 (illustrative — recompute in the live tool for the exact digest):
Paste the same string into ToolVerse Hash Generator → select SHA-256 → copy the 64-character hex string.

Integrity workflow:
1) Publish file + sha256sum
2) Downloader recomputes hash
3) Match → safe to use; mismatch → re-download or investigate tampering`,
    faqs: [
      {
        question: "Which hash algorithm should I use in 2026?",
        answer:
          "For integrity checks, SHA-256 or SHA-512 are widely accepted. Avoid MD5 and SHA-1 for security-sensitive collision resistance. For passwords, use a slow password hash, not a general SHA digest.",
      },
      {
        question: "Why do two tools give different hashes for the same text?",
        answer:
          "Differences in line endings (CRLF vs LF), trailing newlines, or UTF-8 vs another encoding change the bytes. Normalize input before comparing digests.",
      },
      {
        question: "Can hashing prove who authored a file?",
        answer:
          "No. A hash proves integrity of content, not authorship. Digital signatures combine hashing with private keys to assert identity.",
      },
      {
        question: "Is it safe to hash secrets in the browser?",
        answer:
          "For learning and non-sensitive demos, yes. For production secrets and regulated data, follow your security policy—local CLI tools or approved vaults may be required.",
      },
      {
        question: "What is a checksum versus a cryptographic hash?",
        answer:
          "Checksums (like simple CRC) catch accidental corruption. Cryptographic hashes resist intentional collision attacks. Use cryptographic hashes when an adversary might be involved.",
      },
    ],
    updatedAt: UPDATED_AT,
  },

  "jwt-decoder": {
    whatIs: `JSON Web Tokens (JWTs) package claims—user IDs, roles, expiry times—into a compact, URL-safe string with three Base64URL segments: header, payload, and signature. A JWT decoder lets you inspect the header and payload without calling an API, which is invaluable when debugging login flows, API gateways, and mobile clients.

Decoding is not the same as verifying. Anyone can read an unsigned or improperly validated token’s payload. Signature verification requires the correct secret or public key and must happen on a trusted server. The ToolVerse JWT Decoder at tool-verse.online focuses on safe inspection: see algorithms, expiry (exp), issued-at (iat), and custom claims so you can spot misconfigurations fast.

Common issues jump out immediately—tokens signed with none, clocks skewing exp checks, oversized claims bloating cookies, and audience (aud) mismatches between services. Keeping a decoder open during auth work shortens those incident loops.`,
    howTo: [
      "Copy the full JWT string (three segments separated by periods) from your client or logs.",
      "Paste it into the ToolVerse JWT Decoder.",
      "Inspect the decoded header for alg and typ values.",
      "Review the payload claims: sub, exp, iat, aud, and any custom fields.",
      "Check whether exp is still in the future relative to your environment’s clock.",
      "Remember: decoding locally does not prove the signature is valid—verify on the server.",
    ],
    benefits: [
      "Debug auth failures without redeploying services.",
      "Confirm claim shapes during API contract reviews.",
      "Spot dangerous algorithms or missing expiry early.",
      "Teach teammates JWT structure with real tokens from staging.",
      "Reduce back-and-forth when mobile and web clients disagree on session state.",
    ],
    useCases: [
      "Investigating 401 responses after a token refresh change.",
      "Auditing whether PII is leaking into JWT payloads.",
      "Comparing access versus refresh token claim sets.",
      "Validating that feature-flag claims reach edge middleware.",
      "Preparing redacted examples for security documentation.",
    ],
    example: `Token shape:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0IiwibmFtZSI6IkFsZXgiLCJleHAiOjE3ODc5MDAwMDB9.<signature>

Decoded header:
{ "alg": "HS256", "typ": "JWT" }

Decoded payload (example):
{ "sub": "1234", "name": "Alex", "exp": 1787900000 }

Checklist: Is alg expected? Is exp valid? Are claims minimal? Is verification enforced server-side?`,
    faqs: [
      {
        question: "Does decoding a JWT verify it?",
        answer:
          "No. Decoding only Base64URL-decodes the header and payload. Verification checks the signature with a secret or public key and must be performed by your backend or trusted library.",
      },
      {
        question: "Is it safe to paste production JWTs into an online decoder?",
        answer:
          "Prefer staging tokens. Production JWTs can grant access until they expire. If you must inspect one, use a privacy-respecting local or client-side tool and rotate if exposure is a concern.",
      },
      {
        question: "What does alg set to none mean?",
        answer:
          "It indicates an unsecured JWT. Reject such tokens in production verifiers. Attackers historically abused libraries that accepted none unexpectedly.",
      },
      {
        question: "Why is my token rejected even though exp looks fine?",
        answer:
          "Clock skew, wrong audience, issuer mismatch, or signature key rotation are common causes. Inspect claims carefully and confirm the verifier configuration.",
      },
      {
        question: "Should I store JWTs in localStorage?",
        answer:
          "It depends on your threat model. HttpOnly secure cookies reduce XSS token theft risk; localStorage is simpler but more exposed to script injection. Follow your security guidelines.",
      },
    ],
    updatedAt: UPDATED_AT,
  },

  "lorem-ipsum": {
    whatIs: `Lorem Ipsum generators produce placeholder copy that mimics the rhythm of real paragraphs without distracting reviewers with unfinished marketing text. Designers drop it into wireframes; front-end engineers fill components while waiting on final content; product managers mock long-form layouts to test wrapping and truncation.

Good placeholder text is not random keyboard smash. Classic Lorem Ipsum descends from scrambled Latin, giving realistic word lengths and punctuation patterns. The ToolVerse Lorem Ipsum tool at tool-verse.online lets you request paragraphs, sentences, or word counts sized to the layout you are testing.

Using realistic filler early prevents a class of UI bugs: buttons that break with long German words, cards that collapse with empty states, and SEO previews that assume short titles. Generate once, paste into your mock, and keep building.`,
    howTo: [
      "Open the Lorem Ipsum generator on ToolVerse.",
      "Choose whether you need words, sentences, or full paragraphs.",
      "Set the quantity to match the space in your design or component.",
      "Generate the text and copy it into Figma, your CMS draft, or JSX.",
      "Replace placeholders with final copy before launch—never ship Lorem to production.",
      "Regenerate with a larger count when stress-testing overflow and line clamps.",
    ],
    benefits: [
      "Prototype layouts without waiting on final editorial copy.",
      "Stress-test truncation, line height, and responsive wrapping.",
      "Keep stakeholder reviews focused on structure instead of draft wording.",
      "Fill CMS fields quickly during theme or template development.",
      "Create consistent sample data across design and engineering mocks.",
    ],
    useCases: [
      "Populating blog card grids before articles exist.",
      "Testing email templates with multi-paragraph bodies.",
      "Demoing a CMS rich-text field in a sales walkthrough.",
      "Checking how a mobile nav handles long menu labels via sentence mode.",
      "Seeding Storybook stories with predictable filler paragraphs.",
    ],
    example: `Request: 2 paragraphs

Sample output:
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Use paragraph mode for article bodies; use word mode when you only need a 12-word excerpt for a card.`,
    faqs: [
      {
        question: "Is Lorem Ipsum real Latin?",
        answer:
          "It is derived from classical Latin but scrambled and altered. It is not meant to be read as meaningful prose—only as visual filler.",
      },
      {
        question: "Can I use Lorem Ipsum in production?",
        answer:
          "You should not. Search engines and users treat placeholder text as a quality issue. Replace it with real content before publishing.",
      },
      {
        question: "Why not just repeat “text text text”?",
        answer:
          "Uniform words hide wrapping and hyphenation issues. Lorem-like distributions expose layout problems earlier.",
      },
      {
        question: "Does ToolVerse store the generated text?",
        answer:
          "Generation is ephemeral for typical use. Treat anything you paste into designs as non-sensitive; placeholders should never include real customer data.",
      },
      {
        question: "Can I generate text in other languages?",
        answer:
          "Classic generators focus on Lorem Ipsum. For locale-specific length testing, use real sample copy in that language when possible.",
      },
    ],
    updatedAt: UPDATED_AT,
  },

  "markdown-preview": {
    whatIs: `Markdown preview tools render plain-text Markdown as formatted HTML so you can see headings, lists, links, code blocks, and emphasis before publishing. Writers draft in Markdown for portability; developers keep README files and docs-as-code in the same format. A live preview closes the gap between syntax and final look.

Different processors disagree on edge cases—tables, task lists, autolinks, and fenced code attributes. Previewing on ToolVerse at tool-verse.online helps you catch broken links, nested list mistakes, and unclosed code fences before a pull request review becomes a formatting debate.

Markdown remains the lingua franca of GitHub, Notion exports, static sites, and many CMS pipelines. Having a fast, distraction-free preview means you can draft offline-style text and still ship polished documentation.`,
    howTo: [
      "Open the Markdown Preview tool and paste your Markdown source.",
      "Watch the rendered output update as you edit headings, lists, and code fences.",
      "Fix any broken links or list indentation issues you spot in the preview.",
      "Copy the source back into your repository, CMS, or documentation platform.",
      "If your target platform uses a Markdown dialect (GFM, CommonMark), spot-check platform-specific features there too.",
      "Keep images referenced with valid URLs so previews show real assets.",
    ],
    benefits: [
      "Catch formatting mistakes before reviewers do.",
      "Draft README and docs without committing trial-and-error pushes.",
      "Visualize code blocks and tables that are hard to parse as raw text.",
      "Speed up content edits for blogs that accept Markdown.",
      "Teach Markdown syntax with instant visual feedback.",
    ],
    useCases: [
      "Polishing a GitHub README before opening a repository to the public.",
      "Checking changelog formatting for a release announcement.",
      "Previewing blog drafts destined for a static site generator.",
      "Validating nested task lists in a project brief.",
      "Reviewing API documentation snippets with fenced examples.",
    ],
    example: `Markdown input:
## Install
Run \`npm i\` then start the app.

- Fast preview
- Portable source

\`\`\`ts
export const greet = (name: string) => \`Hi, \${name}\`;
\`\`\`

Rendered result shows a level-2 heading, an inline code span, a bullet list, and a TypeScript code block—confirm spacing and fences before you commit.`,
    faqs: [
      {
        question: "Which Markdown flavor does the preview use?",
        answer:
          "Many web previews align with GitHub Flavored Markdown (tables, strikethrough, task lists). If your publisher is stricter CommonMark, verify ambiguous syntax on the destination platform.",
      },
      {
        question: "Why do my images not show?",
        answer:
          "Relative paths may not resolve in a generic preview. Use absolute URLs for a quick check, then restore repository-relative paths for production docs.",
      },
      {
        question: "Can I preview HTML embedded in Markdown?",
        answer:
          "Some processors allow raw HTML; others sanitize it. Prefer pure Markdown when you need maximum portability.",
      },
      {
        question: "Does previewing execute JavaScript in code blocks?",
        answer:
          "No. Code blocks are displayed as text. Never assume a preview environment runs untrusted scripts.",
      },
      {
        question: "How do I escape Markdown characters?",
        answer:
          "Prefix special characters with a backslash, or wrap them in inline code spans when you want them shown literally.",
      },
    ],
    updatedAt: UPDATED_AT,
  },

  "url-encoder": {
    whatIs: `URL encoding (percent-encoding) replaces unsafe or reserved characters with %HH sequences so they travel safely inside URLs and form bodies. Spaces become %20 (or + in some form encodings), ampersands and equals signs get encoded when they are data rather than delimiters, and non-ASCII text is expressed as UTF-8 bytes then percent-encoded.

Without encoding, query strings break: a search term containing & truncates parameters, and internationalized text can corrupt routing. The ToolVerse URL Encoder at tool-verse.online helps you encode or decode strings deliberately—essential when building share links, OAuth redirects, or webhook callbacks.

Developers also confuse encodeURI and encodeURIComponent semantics. Encoding a full URL differs from encoding a single query value. A dedicated tool makes that distinction obvious and prevents the classic “double-encoded %25” mess in logs.`,
    howTo: [
      "Open the URL Encoder and paste the raw string or query value.",
      "Choose encode to percent-encode reserved characters for safe inclusion in a URL.",
      "Choose decode to reverse %HH sequences back into readable text.",
      "Copy the result into your link builder, redirect URI, or API client.",
      "Encode each query parameter value separately—do not blindly encode an entire URL if you still need structural ? and & characters.",
      "Verify the final link in a browser address bar or HTTP client before shipping.",
    ],
    benefits: [
      "Prevent broken query strings caused by reserved characters.",
      "Handle international text in links without corruption.",
      "Debug double-encoding issues in redirect chains.",
      "Build correct OAuth and webhook callback URLs faster.",
      "Teach juniors the difference between path and component encoding.",
    ],
    useCases: [
      "Encoding a search query that includes spaces and punctuation.",
      "Preparing redirect_uri values for OAuth providers.",
      "Decoding mysterious % sequences found in analytics logs.",
      "Building mailto or share links with prefilled subject lines.",
      "Fixing CMS-generated URLs that were incorrectly escaped twice.",
    ],
    example: `Raw query value:
blue & green tools / 2026

Encoded (component style):
blue%20%26%20green%20tools%20%2F%202026

Full URL assembly:
https://tool-verse.online/search?q=blue%20%26%20green%20tools%20%2F%202026

Decode the q parameter alone when inspecting logs—decoding the entire URL string can also decode structural separators you still need.`,
    faqs: [
      {
        question: "Should I use + or %20 for spaces?",
        answer:
          "In application/x-www-form-urlencoded bodies, + often represents a space. In modern URL query components, %20 is clearer and widely accepted. Follow the spec of the API you call.",
      },
      {
        question: "Why is my URL encoded twice?",
        answer:
          "A layer encoded an already-encoded value, turning % into %25. Decode once carefully or fix the layer that re-encodes blindly.",
      },
      {
        question: "Do I encode the entire URL?",
        answer:
          "Usually no. Keep scheme, host, and delimiters intact. Encode path segments and query values individually as required.",
      },
      {
        question: "How are non-English characters encoded?",
        answer:
          "They are converted to UTF-8 bytes, then each byte is percent-encoded. Decoding restores the original Unicode text when UTF-8 is assumed.",
      },
      {
        question: "Is URL encoding the same as HTML escaping?",
        answer:
          "No. HTML escaping turns < into &lt; for markup safety. URL encoding prepares data for URLs. Use the right transform for the context.",
      },
    ],
    updatedAt: UPDATED_AT,
  },

  "uuid-generator": {
    whatIs: `A UUID (Universally Unique Identifier) is a 128-bit value typically displayed as 32 hexadecimal digits grouped with hyphens. Applications use UUIDs for database primary keys, distributed tracing, idempotency keys, and resource names where a central sequence generator would create contention.

Version 4 UUIDs rely on random bits and are the everyday choice for most apps. Version 7 (where supported) introduces time-ordered values that improve index locality. The ToolVerse UUID Generator at tool-verse.online creates one or many IDs instantly so you can seed fixtures, test imports, or prototype APIs without wiring a library first.

UUIDs are unique for practical purposes when generated correctly, but they are not secret. Do not treat them as authentication tokens. Pair them with proper auth and authorization whenever they identify sensitive resources.`,
    howTo: [
      "Open the UUID Generator on ToolVerse.",
      "Select the UUID version your system expects (commonly version 4).",
      "Choose how many IDs to generate for bulk seeding.",
      "Copy a single UUID or the full list into your database seed, test file, or ticket.",
      "Confirm your storage column width (36 characters with hyphens, or 32 without).",
      "Avoid generating IDs client-side for security-sensitive allocation if your architecture requires server authority.",
    ],
    benefits: [
      "Create collision-resistant IDs without a central counter.",
      "Seed demos and tests with realistic primary keys.",
      "Support distributed systems that cannot share auto-increment sequences.",
      "Generate bulk IDs for CSV imports and migration rehearsals.",
      "Standardize on a canonical string format across services.",
    ],
    useCases: [
      "Assigning IDs to records before an offline-capable client syncs.",
      "Creating idempotency keys for payment or form submissions.",
      "Labeling trace and span IDs during observability experiments.",
      "Populating Storybook mocks with stable entity identifiers.",
      "Migrating from integer keys to UUIDs in a staging database.",
    ],
    example: `Generated UUID v4 examples:
3f8a2c1e-9b4d-4e2a-8c7f-1a2b3c4d5e6f
a91c0e77-2d55-4b10-9f3a-88e1c0b7d4a2

SQL sketch:
INSERT INTO projects (id, name)
VALUES ('3f8a2c1e-9b4d-4e2a-8c7f-1a2b3c4d5e6f', 'ToolVerse Demo');

Bulk tip: generate 50 IDs, paste into a spreadsheet column, then map rows during a CSV import dry run.`,
    faqs: [
      {
        question: "Can two UUIDs ever collide?",
        answer:
          "For version 4, collision probability is astronomically low when generators use sufficient randomness. Still, enforce uniqueness constraints in your database as a safety net.",
      },
      {
        question: "Should I store UUIDs with hyphens?",
        answer:
          "Both forms are common. Pick one canonical representation in your API and database to avoid subtle mismatches in lookups.",
      },
      {
        question: "Are UUIDs secure tokens?",
        answer:
          "No. They identify resources; they do not authenticate users. Guessing risk is low for v4, but authorization checks are still mandatory.",
      },
      {
        question: "UUID v4 vs v7—what should I pick?",
        answer:
          "Use v4 for maximum compatibility. Consider v7 when you want time-sortable IDs and your stack supports the newer version.",
      },
      {
        question: "Why do some systems strip UUID hyphens?",
        answer:
          "Binary or compact storage sometimes stores 16 raw bytes or 32 hex characters. Convert carefully when integrating with those systems.",
      },
    ],
    updatedAt: UPDATED_AT,
  },

  "word-counter": {
    whatIs: `A word counter tallies words, characters, sentences, and often reading time so writers and marketers can hit brief requirements without manual counting. Blog posts, meta descriptions, academic abstracts, and social captions each have different length constraints—and exceeding them can truncate previews or weaken SEO.

The ToolVerse Word Counter at tool-verse.online updates as you type or paste, making it easy to trim fluff, expand thin drafts, or split a long article into scannable sections. Character counts with and without spaces matter for SMS, ads, and title tags; sentence and paragraph stats help editors judge pacing.

Beyond marketing, developers use counters when enforcing form limits, validating CMS fields, and estimating localization expansion. A reliable counter becomes a small but constant companion in content workflows.`,
    howTo: [
      "Open the Word Counter and paste your draft into the input area.",
      "Read the live totals for words, characters, and related metrics.",
      "Trim or expand sections until you meet the brief (for example 150–160 characters for a meta description).",
      "Use sentence and paragraph stats to find dense spots that need rewriting.",
      "Copy the revised text back into your CMS or document.",
      "Recheck after editorial changes—small wording edits can tip you over platform limits.",
    ],
    benefits: [
      "Hit SEO and ad length limits with confidence.",
      "Estimate reading time for blog headers and newsletters.",
      "Improve pacing by spotting overly long sentences.",
      "Enforce form and CMS constraints during content QA.",
      "Compare draft versions quantitatively during editing passes.",
    ],
    useCases: [
      "Crafting title tags and meta descriptions within pixel/character budgets.",
      "Keeping LinkedIn or X posts inside platform limits before publishing.",
      "Checking student essays against assignment word ranges.",
      "Validating product descriptions for marketplace maximums.",
      "Preparing speaker notes with a target spoken-word duration.",
    ],
    example: `Sample paragraph:
ToolVerse helps you ship everyday utilities from tool-verse.online without installing desktop software.

Approximate stats you might see:
Words: 14
Characters (with spaces): ~90
Characters (without spaces): ~78

Meta description workflow:
1) Paste draft description
2) Trim to ~155 characters
3) Ensure the primary keyword appears naturally
4) Copy into your SEO plugin`,
    faqs: [
      {
        question: "How does the tool define a word?",
        answer:
          "Typically by splitting on whitespace and punctuation boundaries. Hyphenated compounds and numbers may count differently across tools—use one counter consistently for a project.",
      },
      {
        question: "Do characters include spaces?",
        answer:
          "Counters usually show both figures. Title tags and SMS often care about characters including spaces; some academic limits exclude them—check your brief.",
      },
      {
        question: "How is reading time estimated?",
        answer:
          "Most tools divide word count by an assumed reading speed (often 200–250 words per minute). Treat it as an estimate, not a guarantee.",
      },
      {
        question: "Does Markdown syntax count as words?",
        answer:
          "If you paste raw Markdown, syntax characters may inflate counts. Preview or strip markup when you need content-only statistics.",
      },
      {
        question: "Can I count words in other languages?",
        answer:
          "Latin-script languages work well with whitespace splitting. Languages without spaces between words may need specialized segmenters; verify results for CJK text.",
      },
    ],
    updatedAt: UPDATED_AT,
  },
};

export function getToolGuide(slug: string): ToolGuide | undefined {
  return TOOL_GUIDES[slug];
}
