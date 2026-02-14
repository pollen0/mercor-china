#!/usr/bin/env npx tsx
/**
 * Generic Playwright scraper for Consider-powered VC job boards.
 *
 * Usage:
 *   cd apps/web
 *
 *   # Scrape Kleiner Perkins
 *   npx tsx scripts/scrape-consider.ts \
 *     --url "https://jobs.kleinerperkins.com" \
 *     --firm "Kleiner Perkins" \
 *     --output "../api/scripts/data/kpcb.json"
 *
 *   # Scrape NEA
 *   npx tsx scripts/scrape-consider.ts \
 *     --url "https://careers.nea.com" \
 *     --firm "NEA" \
 *     --output "../api/scripts/data/nea.json"
 *
 *   # Discovery mode (inspect DOM)
 *   npx tsx scripts/scrape-consider.ts \
 *     --url "https://jobs.kleinerperkins.com" \
 *     --firm "Kleiner Perkins" --discover
 *
 *   # Headed mode (see the browser)
 *   npx tsx scripts/scrape-consider.ts \
 *     --url "https://jobs.kleinerperkins.com" \
 *     --firm "Kleiner Perkins" \
 *     --output "../api/scripts/data/kpcb.json" --headed
 */

import { chromium, type Page, type Browser } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Types
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

interface JobCard {
  company: string;
  title: string;
  location: string;
  tags: string[];
  detailUrl: string;
  description?: string;
  requirements?: string[];
  salary?: string;
  applyUrl?: string;
  companyMeta?: {
    slug: string;
    description: string;
    stage: string;
    size: string;
    industries: string[];
    hqLocation: string;
  };
}

interface ScrapeOutput {
  metadata: {
    boardUrl: string;
    vcFirm: string;
    scrapedAt: string;
    totalJobsOnBoard: number;
    usInternJobs: number;
  };
  jobs: JobCard[];
}

interface CliArgs {
  url: string;
  firm: string;
  output: string;
  discover: boolean;
  scrapeDetails: boolean;
  delay: number;
  headed: boolean;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// CLI arg parsing
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function parseArgs(): CliArgs {
  const args = process.argv.slice(2);
  const parsed: CliArgs = {
    url: "",
    firm: "",
    output: "",
    discover: false,
    scrapeDetails: false,
    delay: 500,
    headed: false,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--url":
        parsed.url = args[++i];
        break;
      case "--firm":
        parsed.firm = args[++i];
        break;
      case "--output":
        parsed.output = args[++i];
        break;
      case "--discover":
        parsed.discover = true;
        break;
      case "--scrape-details":
        parsed.scrapeDetails = true;
        break;
      case "--delay":
        parsed.delay = parseInt(args[++i], 10);
        break;
      case "--headed":
        parsed.headed = true;
        break;
    }
  }

  if (!parsed.url || !parsed.firm) {
    console.error("Usage: npx tsx scripts/scrape-consider.ts --url <URL> --firm <FIRM> [OPTIONS]");
    console.error("");
    console.error("Required:");
    console.error("  --url <URL>          Board URL (e.g., https://jobs.kleinerperkins.com)");
    console.error("  --firm <FIRM>        VC firm name (e.g., \"Kleiner Perkins\")");
    console.error("");
    console.error("Modes:");
    console.error("  --discover           Dump rendered HTML for DOM inspection");
    console.error("  --output <FILE>      Scrape and write JSON output");
    console.error("");
    console.error("Options:");
    console.error("  --scrape-details     Visit each job page for full description");
    console.error("  --delay <MS>         Delay between detail page requests (default: 500)");
    console.error("  --headed             Run with visible browser window");
    process.exit(1);
  }

  if (!parsed.discover && !parsed.output) {
    console.error("Error: Must specify --discover or --output <FILE>");
    process.exit(1);
  }

  return parsed;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// US location detection (shared with Getro scraper)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const US_STATE_ABBREVS = new Set([
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
  "DC",
]);

const US_KEYWORDS = [
  "united states", "usa", "u.s.", "remote",
  "san francisco", "new york", "los angeles", "chicago", "seattle",
  "austin", "boston", "denver", "atlanta", "miami", "portland",
  "san jose", "san diego", "philadelphia", "phoenix", "dallas",
  "houston", "washington", "minneapolis", "nashville", "charlotte",
  "raleigh", "salt lake", "pittsburgh", "detroit", "columbus",
  "indianapolis", "milwaukee", "kansas city", "st. louis",
  "mountain view", "palo alto", "menlo park", "sunnyvale",
  "cupertino", "redwood city", "santa clara", "irvine",
  "cambridge", "brooklyn", "manhattan",
];

const NON_US_KEYWORDS = [
  "india", "uk", "united kingdom", "london", "singapore", "germany",
  "berlin", "france", "paris", "canada", "toronto", "vancouver",
  "australia", "sydney", "melbourne", "japan", "tokyo", "china",
  "beijing", "shanghai", "brazil", "mexico", "ireland", "dublin",
  "netherlands", "amsterdam", "sweden", "stockholm", "israel",
  "tel aviv", "korea", "seoul", "taiwan", "hong kong", "bangalore",
  "hyderabad", "mumbai", "pune", "noida", "gurgaon", "chennai",
];

function isUSLocation(location: string): boolean {
  if (!location) return false;
  const lower = location.toLowerCase().trim();

  for (const kw of NON_US_KEYWORDS) {
    if (lower.includes(kw)) return false;
  }

  const parts = lower.split(/[,\s]+/);
  for (const part of parts) {
    if (US_STATE_ABBREVS.has(part.toUpperCase())) return true;
  }

  for (const kw of US_KEYWORDS) {
    if (lower.includes(kw)) return true;
  }

  return false;
}

function isInternTitle(title: string): boolean {
  const lower = title.toLowerCase();
  return lower.includes("intern") || lower.includes("internship");
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Consider portal: navigate and wait for content
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function navigateAndWait(page: Page, boardUrl: string): Promise<void> {
  const internUrl = `${boardUrl}/jobs?titlePrefix=intern&internshipOnly=true`;
  console.log(`Navigating to ${internUrl}...`);
  await page.goto(internUrl, { waitUntil: "domcontentloaded", timeout: 60000 });

  // Wait for React SPA to hydrate and load job data
  console.log("Waiting for SPA to render...");
  await page.waitForTimeout(5000);

  // Wait for network to settle (Consider fetches job data via API)
  try {
    await page.waitForLoadState("networkidle", { timeout: 15000 });
  } catch {
    console.log("  Network didn't fully settle — continuing anyway");
  }

  // Additional wait for any lazy rendering
  await page.waitForTimeout(2000);
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Scroll to load all results
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function loadAllResults(page: Page): Promise<void> {
  console.log("Loading all results via scrolling / load-more...");

  // First, try to enable "Internships only" toggle if it's not already active
  await page.evaluate(() => {
    const toggles = document.querySelectorAll(".boards-toggle-text, button");
    toggles.forEach((el) => {
      if (el.textContent?.toLowerCase().includes("internships only")) {
        const btn = el.closest("button") || el;
        // Only click if it's not already active
        const isActive = btn.classList.contains("active") ||
          btn.getAttribute("aria-pressed") === "true";
        if (!isActive) (btn as HTMLElement).click();
      }
    });
  });
  await page.waitForTimeout(2000);

  let round = 0;
  let noProgressCount = 0;
  const maxNoProgress = 5;

  while (noProgressCount < maxNoProgress) {
    round++;

    // Count current visible job items using Consider-specific selectors
    const beforeCount = await page.evaluate(
      () => document.querySelectorAll(".job-list-job").length
    );

    // Try "Load more" / "Show more" buttons
    const loadMoreClicked = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      for (const btn of btns) {
        const text = btn.textContent?.toLowerCase() || "";
        if (
          text.includes("load more") ||
          text.includes("show more") ||
          text.includes("view more") ||
          text.includes("see more")
        ) {
          btn.click();
          return true;
        }
      }
      return false;
    });

    if (!loadMoreClicked) {
      // Scroll to bottom as fallback
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    }

    await page.waitForTimeout(2000);
    try {
      await page.waitForLoadState("networkidle", { timeout: 5000 });
    } catch {
      // Fine
    }

    const afterCount = await page.evaluate(
      () => document.querySelectorAll(".job-list-job").length
    );

    if (afterCount === beforeCount) {
      noProgressCount++;
    } else {
      noProgressCount = 0;
    }

    const companyCount = await page.evaluate(
      () => document.querySelectorAll(".grouped-job-result").length
    );

    console.log(`  Round ${round}: ${afterCount} jobs across ${companyCount} companies (${noProgressCount}/${maxNoProgress} stale)`);
  }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Discovery mode: dump HTML for DOM inspection
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function discoverDOM(page: Page, firm: string): Promise<void> {
  const dumpDir = path.resolve(__dirname, "../api/scripts/data");
  if (!fs.existsSync(dumpDir)) {
    fs.mkdirSync(dumpDir, { recursive: true });
  }

  const slug = firm.toLowerCase().replace(/\s+/g, "-");

  // Take screenshot
  const screenshotPath = path.join(dumpDir, `${slug}-portal-screenshot.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log(`Screenshot saved to: ${screenshotPath}`);

  // Dump the rendered HTML
  const html = await page.content();
  const htmlPath = path.join(dumpDir, `${slug}-portal-rendered.html`);
  fs.writeFileSync(htmlPath, html);
  console.log(`Rendered HTML saved to: ${htmlPath} (${(html.length / 1024).toFixed(0)} KB)`);

  // Analyze the DOM structure for job-related elements
  const analysis = await page.evaluate(() => {
    const results: Record<string, string[]> = {};

    // Find all elements with job-related class names
    const allEls = document.querySelectorAll("*");
    const jobClasses = new Set<string>();
    const jobDataAttrs = new Set<string>();
    const jobLinks = new Set<string>();

    allEls.forEach((el) => {
      const className = el.className;
      if (typeof className === "string" && className) {
        const classes = className.split(/\s+/);
        for (const cls of classes) {
          const lower = cls.toLowerCase();
          if (
            lower.includes("job") ||
            lower.includes("card") ||
            lower.includes("list") ||
            lower.includes("result") ||
            lower.includes("company") ||
            lower.includes("title") ||
            lower.includes("location") ||
            lower.includes("role")
          ) {
            jobClasses.add(cls);
          }
        }
      }

      // Data attributes
      for (const attr of Array.from(el.attributes)) {
        if (attr.name.startsWith("data-") && attr.name !== "data-reactroot") {
          jobDataAttrs.add(`${attr.name}="${attr.value}"`);
        }
      }

      // Links to job pages
      if (el.tagName === "A") {
        const href = (el as HTMLAnchorElement).getAttribute("href") || "";
        if (href.includes("/job") || href.includes("/position")) {
          jobLinks.add(href);
        }
      }
    });

    results.jobClasses = Array.from(jobClasses).sort().slice(0, 100);
    results.dataAttributes = Array.from(jobDataAttrs).sort().slice(0, 100);
    results.jobLinks = Array.from(jobLinks).sort().slice(0, 50);

    // Look for text content that looks like job titles
    const textNodes: string[] = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node: Node | null;
    while ((node = walker.nextNode())) {
      const text = node.textContent?.trim() || "";
      if (
        text.length > 10 &&
        text.length < 200 &&
        (text.toLowerCase().includes("intern") ||
          text.toLowerCase().includes("engineer") ||
          text.toLowerCase().includes("software"))
      ) {
        const parent = node.parentElement;
        const tag = parent?.tagName || "?";
        const cls = (typeof parent?.className === "string" ? parent.className : "").slice(0, 80);
        textNodes.push(`<${tag} class="${cls}"> ${text}`);
      }
    }
    results.jobTextNodes = textNodes.slice(0, 50);

    return results;
  });

  const analysisPath = path.join(dumpDir, `${slug}-portal-analysis.json`);
  fs.writeFileSync(analysisPath, JSON.stringify(analysis, null, 2));
  console.log(`DOM analysis saved to: ${analysisPath}`);

  // Print summary
  console.log(`\n--- DOM Analysis Summary ---`);
  console.log(`Job-related CSS classes: ${analysis.jobClasses.length}`);
  if (analysis.jobClasses.length > 0) {
    console.log(`  Sample: ${analysis.jobClasses.slice(0, 10).join(", ")}`);
  }
  console.log(`Data attributes: ${analysis.dataAttributes.length}`);
  if (analysis.dataAttributes.length > 0) {
    console.log(`  Sample: ${analysis.dataAttributes.slice(0, 10).join(", ")}`);
  }
  console.log(`Job links: ${analysis.jobLinks.length}`);
  if (analysis.jobLinks.length > 0) {
    console.log(`  Sample: ${analysis.jobLinks.slice(0, 10).join("\n          ")}`);
  }
  console.log(`Job-related text nodes: ${analysis.jobTextNodes.length}`);
  if (analysis.jobTextNodes.length > 0) {
    console.log(`  Sample:`);
    analysis.jobTextNodes.slice(0, 15).forEach((t: string) => console.log(`    ${t}`));
  }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Extract job cards — Consider platform selectors
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// DOM structure (Consider / careers.nea.com):
//
//  div.grouped-job-result
//    div.grouped-job-result-header
//      a[href="/jobs/company-slug"]
//        img[alt="CompanyName logo"].grouped-job-company-logo
//    div.job-boards-company-tags
//      span.job-boards-company-tag-stages        → "Seed"
//      span.job-boards-company-tag               → "10-100 employees"
//      span.job-boards-company-tag-industries     → "AI"
//      span.job-boards-company-tag-locations      → "New York"
//    div.grouped-job-company-description          → company description
//    div.job-list-job  (one per job)
//      div.job-list-job-details
//        h2.job-list-job-title
//          a[href="external-apply-url"]           → job title
//        div.job-list-badges
//          span.job-list-badge-locations           → "City, State"
//          span.job-list-badge-departments         → "Engineering"
//          span.job-list-badge-posted              → "Posted X days ago"
//          span.job-list-badge-remote              → (if remote)
//        div.job-list-job-skills
//          span.job-list-job-skill                → skill tags
//      div.job-salary-tooltip                     → salary info

async function extractJobCards(page: Page): Promise<JobCard[]> {
  console.log("Extracting job cards from Consider-powered board...");

  const jobs = await page.evaluate(() => {
    const results: Array<{
      company: string;
      title: string;
      location: string;
      tags: string[];
      detailUrl: string;
      salary: string;
      companyMeta: {
        slug: string;
        description: string;
        stage: string;
        size: string;
        industries: string[];
        hqLocation: string;
      };
    }> = [];

    // Detect layout: grouped (NEA-style) vs flat (KP-style)
    const companyGroups = document.querySelectorAll(".grouped-job-result");
    const isGrouped = companyGroups.length > 0;

    if (isGrouped) {
      // ── Grouped layout (NEA-style) ──
      // Company groups contain multiple jobs under a shared header
      companyGroups.forEach((group) => {
        const logoImg = group.querySelector(".grouped-job-company-logo") as HTMLImageElement | null;
        const altText = logoImg?.getAttribute("alt") || "";
        const company = altText.replace(/\s*logo$/i, "").trim();

        const headerLink = group.querySelector(".grouped-job-result-header a") as HTMLAnchorElement | null;
        const slug = (headerLink?.getAttribute("href") || "").replace(/\/jobs\/?/, "").split("?")[0];

        const stageEl = group.querySelector(".job-boards-company-tag-stages");
        const stage = stageEl?.textContent?.trim() || "";

        const industryEls = group.querySelectorAll(".job-boards-company-tag-industries");
        const industries = Array.from(industryEls).map((el) => el.textContent?.trim() || "").filter(Boolean);

        const hqLocationEl = group.querySelector(".job-boards-company-tag-locations");
        const hqLocation = hqLocationEl?.textContent?.trim() || "";

        let size = "";
        const allTags = group.querySelectorAll(".job-boards-company-tag");
        allTags.forEach((tag) => {
          const text = tag.textContent?.trim() || "";
          if (text.includes("employees")) size = text;
        });

        const descEl = group.querySelector(".grouped-job-company-description");
        const description = descEl?.textContent?.trim() || "";

        const jobEls = group.querySelectorAll(".job-list-job");
        jobEls.forEach((jobEl) => {
          const titleLink = jobEl.querySelector(".job-list-job-title a") as HTMLAnchorElement | null;
          const title = titleLink?.textContent?.trim() || "";
          const detailUrl = titleLink?.getAttribute("href") || "";
          if (!title) return;

          const locBadge = jobEl.querySelector(".job-list-badge-locations");
          const location = locBadge?.textContent?.trim() || "";
          const deptBadge = jobEl.querySelector(".job-list-badge-departments");
          const dept = deptBadge?.textContent?.trim() || "";
          const remoteBadge = jobEl.querySelector(".job-list-badge-remote");
          const isRemote = !!remoteBadge;
          const skillEls = jobEl.querySelectorAll(".job-list-job-skill");
          const skills = Array.from(skillEls).map((el) => el.textContent?.trim() || "").filter(Boolean);
          const salaryEl = jobEl.querySelector(".job-salary-tooltip-text");
          const salary = salaryEl?.textContent?.trim() || "";

          const tags: string[] = [];
          if (dept) tags.push(dept);
          if (isRemote) tags.push("Remote");
          tags.push(...skills);

          results.push({
            company, title,
            location: isRemote && !location ? "Remote" : location,
            tags, detailUrl, salary,
            companyMeta: { slug, description, stage, size, industries, hqLocation },
          });
        });
      });
    } else {
      // ── Flat layout (KP-style) ──
      // Each .job-list-job has its own company link and logo
      const jobEls = document.querySelectorAll(".job-list-job");

      jobEls.forEach((jobEl) => {
        // Company name from .job-list-job-company-link or logo alt
        const companyLink = jobEl.querySelector(".job-list-job-company-link") as HTMLAnchorElement | null;
        let company = companyLink?.textContent?.trim() || "";
        const slug = (companyLink?.getAttribute("href") || "").replace(/\/jobs\/?/, "").split("?")[0];

        if (!company) {
          const logoImg = jobEl.querySelector(".job-list-job-logo img") as HTMLImageElement | null;
          company = (logoImg?.getAttribute("alt") || "").replace(/\s*logo$/i, "").trim();
        }

        // Title and apply URL
        const titleLink = jobEl.querySelector(".job-list-job-title a") as HTMLAnchorElement | null;
        const title = titleLink?.textContent?.trim() || "";
        const detailUrl = titleLink?.getAttribute("href") || "";
        if (!title) return;

        // Location
        const locBadge = jobEl.querySelector(".job-list-badge-locations");
        const location = locBadge?.textContent?.trim() || "";

        // Department
        const deptBadge = jobEl.querySelector(".job-list-badge-departments");
        const dept = deptBadge?.textContent?.trim() || "";

        // Remote badge
        const remoteBadge = jobEl.querySelector(".job-list-badge-remote");
        const isRemote = !!remoteBadge;

        // Industries from badge
        const industryBadge = jobEl.querySelector(".job-list-badge-industries");
        const industriesText = industryBadge?.textContent?.trim() || "";
        const industries = industriesText ? industriesText.split(",").map((s: string) => s.trim()).filter(Boolean) : [];

        // Stage and size from .job-list-badge-stages (e.g. "Growth, 1000+ employees")
        const stagesBadge = jobEl.querySelector(".job-list-badge-stages");
        const stagesText = stagesBadge?.textContent?.trim() || "";
        let stage = "";
        let size = "";
        if (stagesText) {
          const parts = stagesText.split(",").map((s: string) => s.trim());
          for (const p of parts) {
            if (p.includes("employees")) size = p;
            else if (!stage) stage = p;
          }
        }

        // Skills
        const skillEls = jobEl.querySelectorAll(".job-list-job-skill");
        const skills = Array.from(skillEls).map((el) => el.textContent?.trim() || "").filter(Boolean);

        // Salary tooltip
        const salaryEl = jobEl.querySelector(".job-salary-tooltip-text");
        const salary = salaryEl?.textContent?.trim() || "";

        // Build tags array
        const tags: string[] = [];
        if (dept) tags.push(dept);
        if (isRemote) tags.push("Remote");
        tags.push(...skills);

        results.push({
          company, title,
          location: isRemote && !location ? "Remote" : location,
          tags, detailUrl, salary,
          companyMeta: { slug, description: "", stage, size, industries, hqLocation: "" },
        });
      });
    }

    return results;
  });

  const layoutType = (await page.evaluate(() => document.querySelectorAll(".grouped-job-result").length)) > 0 ? "grouped" : "flat";
  console.log(`Extracted ${jobs.length} jobs from ${new Set(jobs.map((j) => j.company)).size} companies (${layoutType} layout).`);
  return jobs;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Scrape detail page
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function scrapeDetailPage(page: Page, job: JobCard, delay: number): Promise<void> {
  if (!job.detailUrl) return;

  try {
    await page.goto(job.detailUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(3000); // Wait for SPA to render

    const details = await page.evaluate(() => {
      // Description
      const descSelectors = [
        '[class*="description"], [class*="Description"]',
        '[class*="content"], [class*="Content"]',
        '[class*="detail"], [class*="Detail"]',
        'article',
        '.prose',
        'main section',
      ];

      let description = "";
      for (const sel of descSelectors) {
        const el = document.querySelector(sel);
        if (el && (el.textContent?.trim().length || 0) > 50) {
          description = el.textContent?.trim() || "";
          break;
        }
      }

      // Requirements
      const requirements: string[] = [];
      const listItems = document.querySelectorAll(
        '[class*="requirement"] li, [class*="qualification"] li, ul li, ol li'
      );
      listItems.forEach((li) => {
        const text = li.textContent?.trim();
        if (text && text.length > 5 && text.length < 300) {
          requirements.push(text);
        }
      });

      // Salary
      const salaryEl = document.querySelector(
        '[class*="salary"], [class*="Salary"], [class*="compensation"], [class*="Compensation"]'
      );
      const salary = salaryEl?.textContent?.trim() || "";

      // Apply URL
      const applyLink = document.querySelector(
        'a[href*="lever.co"], a[href*="greenhouse.io"], a[href*="ashbyhq.com"], a[href*="workday.com"], a[href*="boards.greenhouse"]'
      );
      const applyUrl = applyLink?.getAttribute("href") || "";

      // Company name (from detail page)
      const companyEl = document.querySelector(
        'a[href*="/companies/"], [class*="company"], [class*="Company"], [class*="employer"], [class*="Employer"]'
      );
      const company = companyEl?.textContent?.trim() || "";

      // Location (from detail page)
      const locationEl = document.querySelector(
        '[class*="location"], [class*="Location"]'
      );
      const location = locationEl?.textContent?.trim() || "";

      return { description, requirements, salary, applyUrl, company, location };
    });

    if (details.description) job.description = details.description.slice(0, 5000);
    if (details.requirements.length > 0) job.requirements = details.requirements.slice(0, 20);
    if (details.salary) job.salary = details.salary;
    if (details.applyUrl) job.applyUrl = details.applyUrl;
    if (!job.company && details.company) job.company = details.company;
    if (!job.location && details.location) job.location = details.location;
  } catch (err) {
    console.error(`  Failed to scrape ${job.detailUrl}: ${err}`);
  }

  if (delay > 0) {
    await page.waitForTimeout(delay);
  }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Main
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function main() {
  const args = parseArgs();
  const boardUrl = args.url.replace(/\/$/, "");

  console.log("=".repeat(60));
  console.log(`Consider Board Scraper — ${args.firm}`);
  console.log(`  Board:  ${boardUrl}`);
  console.log(`  Mode:   ${args.discover ? "Discovery (DOM inspection)" : "Scrape"}`);
  if (args.output) console.log(`  Output: ${args.output}`);
  console.log(`  Browser: ${args.headed ? "Headed (visible)" : "Headless"}`);
  console.log("=".repeat(60));

  // Ensure output directory exists
  if (args.output) {
    const outputDir = path.dirname(args.output);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
  }

  let browser: Browser | null = null;

  try {
    browser = await chromium.launch({ headless: !args.headed });
    const context = await browser.newContext({
      userAgent:
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      viewport: { width: 1280, height: 900 },
    });
    const page = await context.newPage();

    // Navigate and wait for content to render
    await navigateAndWait(page, boardUrl);

    // Discovery mode: dump HTML and analysis
    if (args.discover) {
      await loadAllResults(page);
      await discoverDOM(page, args.firm);
      console.log("\nDiscovery complete! Check the output files to identify DOM selectors.");
      return;
    }

    // Scrape mode
    await loadAllResults(page);

    const allJobs = await extractJobCards(page);
    const totalOnBoard = allJobs.length;
    console.log(`\nTotal jobs extracted: ${totalOnBoard}`);

    // Filter for US intern positions
    const internJobs = allJobs.filter((job) => {
      const titleMatch = isInternTitle(job.title);
      const locationMatch = isUSLocation(job.location);

      if (titleMatch && (!job.location || job.location.toLowerCase().includes("remote"))) {
        return true;
      }

      return titleMatch && locationMatch;
    });

    console.log(`US intern positions: ${internJobs.length}`);

    // Scrape detail pages if requested
    if (args.scrapeDetails && internJobs.length > 0) {
      console.log(`\nScraping detail pages for ${internJobs.length} jobs...`);

      for (let i = 0; i < internJobs.length; i++) {
        const job = internJobs[i];
        console.log(`  [${i + 1}/${internJobs.length}] ${job.company || "?"} — ${job.title}`);
        await scrapeDetailPage(page, job, args.delay);

        if ((i + 1) % 50 === 0 && i + 1 < internJobs.length) {
          console.log(`  -- Pausing 5s after ${i + 1} requests --`);
          await page.waitForTimeout(5000);
        }
      }
    }

    // Build output
    const output: ScrapeOutput = {
      metadata: {
        boardUrl,
        vcFirm: args.firm,
        scrapedAt: new Date().toISOString(),
        totalJobsOnBoard: totalOnBoard,
        usInternJobs: internJobs.length,
      },
      jobs: internJobs,
    };

    // Write JSON
    fs.writeFileSync(args.output, JSON.stringify(output, null, 2));

    console.log(`\n${"=".repeat(60)}`);
    console.log("Scrape complete!");
    console.log(`  Total extracted:  ${totalOnBoard}`);
    console.log(`  US intern jobs:   ${internJobs.length}`);
    console.log(`  Output:           ${args.output}`);
    console.log("=".repeat(60));

    // Print companies found
    const companies = Array.from(new Set(internJobs.map((j) => j.company).filter(Boolean)));
    if (companies.length > 0) {
      console.log(`\nCompanies with intern roles (${companies.length}):`);
      companies.forEach((c) => {
        const count = internJobs.filter((j) => j.company === c).length;
        console.log(`  - ${c} (${count} role${count > 1 ? "s" : ""})`);
      });
    }

    // Also list jobs with empty company names
    const noCompany = internJobs.filter((j) => !j.company);
    if (noCompany.length > 0) {
      console.log(`\nJobs with unknown company (${noCompany.length}):`);
      noCompany.forEach((j) => {
        console.log(`  - ${j.title} | ${j.location} | ${j.detailUrl}`);
      });
    }
  } finally {
    if (browser) await browser.close();
  }
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
