#!/usr/bin/env npx tsx
/**
 * Playwright scraper for Getro-powered VC job boards.
 *
 * Usage:
 *   cd apps/web
 *
 *   # Fast mode: job cards only
 *   npx tsx scripts/scrape-getro.ts \
 *     --url "https://jobs.khoslaventures.com" \
 *     --firm "Khosla Ventures" \
 *     --output "../api/scripts/data/khosla.json"
 *
 *   # Full mode: cards + detail pages
 *   npx tsx scripts/scrape-getro.ts \
 *     --url "https://jobs.khoslaventures.com" \
 *     --firm "Khosla Ventures" \
 *     --output "../api/scripts/data/khosla.json" \
 *     --scrape-details --delay 500
 *
 *   # Resume from checkpoint
 *   npx tsx scripts/scrape-getro.ts \
 *     --url "https://jobs.khoslaventures.com" \
 *     --firm "Khosla Ventures" \
 *     --output "../api/scripts/data/khosla.json" \
 *     --scrape-details --resume
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
  filter?: string;
  scrapeDetails: boolean;
  delay: number;
  resume: boolean;
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
    scrapeDetails: false,
    delay: 500,
    resume: false,
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
      case "--filter":
        parsed.filter = args[++i];
        break;
      case "--scrape-details":
        parsed.scrapeDetails = true;
        break;
      case "--delay":
        parsed.delay = parseInt(args[++i], 10);
        break;
      case "--resume":
        parsed.resume = true;
        break;
    }
  }

  if (!parsed.url || !parsed.firm || !parsed.output) {
    console.error("Usage: npx tsx scripts/scrape-getro.ts --url <URL> --firm <FIRM> --output <FILE>");
    console.error("");
    console.error("Required:");
    console.error("  --url <URL>          Board URL (e.g., https://jobs.khoslaventures.com)");
    console.error("  --firm <FIRM>        VC firm name (e.g., \"Khosla Ventures\")");
    console.error("  --output <FILE>      Output JSON path");
    console.error("");
    console.error("Optional:");
    console.error("  --filter <QUERY>     Filter text to type in search box");
    console.error("  --scrape-details     Visit each job page for full description");
    console.error("  --delay <MS>         Delay between detail page requests (default: 500)");
    console.error("  --resume             Resume from checkpoint file");
    process.exit(1);
  }

  return parsed;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// US location detection
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

  // Reject known non-US locations
  for (const kw of NON_US_KEYWORDS) {
    if (lower.includes(kw)) return false;
  }

  // Check for US state abbreviations (e.g., "CA", "NY")
  const parts = lower.split(/[,\s]+/);
  for (const part of parts) {
    if (US_STATE_ABBREVS.has(part.toUpperCase())) return true;
  }

  // Check for US city/keyword matches
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
// Infinite scroll
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function loadAllJobs(page: Page): Promise<void> {
  console.log("Loading all jobs via 'Load more' button...");

  let round = 0;
  let noProgressCount = 0;
  const maxNoProgress = 3;

  while (noProgressCount < maxNoProgress) {
    round++;

    // Count current jobs
    const beforeCount = await page.evaluate(
      () => document.querySelectorAll('[data-testid="job-list-item"]').length
    );

    // Try clicking the "Load more" button (Getro uses data-testid="load-more")
    const loadMoreBtn = await page.$('[data-testid="load-more"]');
    if (loadMoreBtn) {
      try {
        await loadMoreBtn.click();
        // Wait for new jobs to render
        await page.waitForTimeout(2000);
        try {
          await page.waitForLoadState("networkidle", { timeout: 5000 });
        } catch {
          // Fine — persistent connections may prevent idle
        }
      } catch {
        // Button may have disappeared
      }
    } else {
      // No load-more button — try scrolling as fallback
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(2000);
    }

    const afterCount = await page.evaluate(
      () => document.querySelectorAll('[data-testid="job-list-item"]').length
    );

    if (afterCount === beforeCount) {
      noProgressCount++;
    } else {
      noProgressCount = 0;
    }

    console.log(`  Round ${round}: ${afterCount} jobs loaded (${noProgressCount}/${maxNoProgress} stale)`);
  }

  const finalCount = await page.evaluate(
    () => document.querySelectorAll('[data-testid="job-list-item"]').length
  );
  console.log(`Loading complete — ${finalCount} job cards on page.`);
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Extract job cards from page
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function extractJobCards(page: Page, boardUrl: string): Promise<JobCard[]> {
  console.log("Extracting job cards from page...");

  const jobs = await page.evaluate((baseUrl: string) => {
    const results: Array<{
      company: string;
      title: string;
      location: string;
      tags: string[];
      detailUrl: string;
    }> = [];

    // Getro boards use data-testid="job-list-item" for each card
    const cards = document.querySelectorAll('[data-testid="job-list-item"]');

    if (cards.length === 0) {
      // Fallback: try link-based extraction
      const jobLinks = document.querySelectorAll('a[href*="/jobs/"]');
      const seen = new Set<string>();

      jobLinks.forEach((link) => {
        const anchor = link as HTMLAnchorElement;
        const href = anchor.getAttribute("href") || "";
        if (!href || href === "/jobs" || href === "/jobs/" || seen.has(href)) return;
        seen.add(href);

        const title = anchor.querySelector('[itemprop="title"]')?.textContent?.trim()
          || anchor.textContent?.trim() || "";
        if (!title || title.startsWith("Read more")) return;

        results.push({
          company: "",
          title,
          location: "",
          tags: [],
          detailUrl: href.startsWith("http") ? href : `${baseUrl}${href}`,
        });
      });

      return results;
    }

    // Process Getro job cards
    cards.forEach((card) => {
      // Title: a[data-testid="job-title-link"] > [itemprop="title"]
      const titleEl = card.querySelector('[data-testid="job-title-link"] [itemprop="title"]')
        || card.querySelector('[data-testid="job-title-link"]');
      const title = titleEl?.textContent?.trim() || "";
      if (!title) return;

      // Detail URL: a[data-testid="job-title-link"] href
      const titleLink = card.querySelector('[data-testid="job-title-link"]') as HTMLAnchorElement | null;
      const href = titleLink?.getAttribute("href") || "";

      // Company: meta[itemprop="name"] or a[data-testid="link"]
      const companyMeta = card.querySelector('meta[itemprop="name"]');
      const companyLink = card.querySelector('[data-testid="link"]');
      const company = companyMeta?.getAttribute("content")
        || companyLink?.textContent?.trim() || "";

      // Location: meta[itemprop="addressLocality"] (most reliable, in hidden schema.org markup)
      const locationMeta = card.querySelector('meta[itemprop="addressLocality"]');
      const location = locationMeta?.getAttribute("content") || "";

      // Tags: div[data-testid="tag"]
      const tagEls = card.querySelectorAll('[data-testid="tag"]');
      const tags = Array.from(tagEls).map((t) => t.textContent?.trim() || "").filter(Boolean);

      results.push({
        company,
        title,
        location,
        tags,
        detailUrl: href.startsWith("http") ? href : href ? `${baseUrl}${href}` : "",
      });
    });

    return results;
  }, boardUrl);

  console.log(`Extracted ${jobs.length} raw job cards.`);
  return jobs;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Scrape detail page
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function scrapeDetailPage(
  page: Page,
  job: JobCard,
  delay: number
): Promise<void> {
  if (!job.detailUrl) return;

  try {
    await page.goto(job.detailUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(1500); // Let JS render

    const details = await page.evaluate(() => {
      // Description — try multiple selectors
      const descSelectors = [
        '[class*="description"], [class*="Description"]',
        '[data-testid*="description"]',
        '[class*="job-detail"], [class*="JobDetail"]',
        '[class*="content"], [class*="Content"]',
        "article",
        ".prose",
        "main section",
      ];

      let descriptionText = "";
      for (const sel of descSelectors) {
        const el = document.querySelector(sel);
        if (el && (el.textContent?.trim().length || 0) > 50) {
          descriptionText = el.textContent?.trim() || "";
          break;
        }
      }

      // Requirements — look for lists within the description
      const requirements: string[] = [];
      const listItems = document.querySelectorAll(
        '[class*="requirement"] li, [class*="qualification"] li, [class*="description"] ul li, article ul li'
      );
      listItems.forEach((li) => {
        const text = li.textContent?.trim();
        if (text && text.length > 5 && text.length < 300) {
          requirements.push(text);
        }
      });

      // Salary
      const salaryEl = document.querySelector(
        '[class*="salary"], [class*="Salary"], [class*="compensation"], [class*="Compensation"], [class*="pay"]'
      );
      const salary = salaryEl?.textContent?.trim() || "";

      // Apply URL
      const applyLink = document.querySelector(
        'a[href*="lever.co"], a[href*="greenhouse.io"], a[href*="ashbyhq.com"], a[href*="workday.com"], a[href*="jobs.lever"], a[href*="boards.greenhouse"], a:has-text("Apply"), a[class*="apply"], a[class*="Apply"]'
      );
      const applyUrl = applyLink?.getAttribute("href") || "";

      // If no company was found on the card, try the detail page
      const companyEl = document.querySelector(
        '[class*="company-name"], [class*="CompanyName"], [class*="employer"], [class*="Employer"], [data-testid*="company"]'
      );
      const company = companyEl?.textContent?.trim() || "";

      // If no location was found on the card, try the detail page
      const locationEl = document.querySelector(
        '[class*="location"], [class*="Location"], [data-testid*="location"]'
      );
      const location = locationEl?.textContent?.trim() || "";

      return { description: descriptionText, requirements, salary, applyUrl, company, location };
    });

    if (details.description) job.description = details.description.slice(0, 5000);
    if (details.requirements.length > 0) job.requirements = details.requirements.slice(0, 20);
    if (details.salary) job.salary = details.salary;
    if (details.applyUrl) job.applyUrl = details.applyUrl;
    if (!job.company && details.company) job.company = details.company;
    if (!job.location && details.location) job.location = details.location;
  } catch (err) {
    console.error(`  Failed to scrape detail page ${job.detailUrl}: ${err}`);
  }

  // Rate limiting
  if (delay > 0) {
    await page.waitForTimeout(delay);
  }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Checkpoint support
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function getCheckpointPath(outputPath: string): string {
  const dir = path.dirname(outputPath);
  const base = path.basename(outputPath, ".json");
  return path.join(dir, `${base}.checkpoint.json`);
}

function saveCheckpoint(checkpointPath: string, jobs: JobCard[], lastIndex: number): void {
  fs.writeFileSync(
    checkpointPath,
    JSON.stringify({ lastIndex, jobs }, null, 2)
  );
}

function loadCheckpoint(checkpointPath: string): { lastIndex: number; jobs: JobCard[] } | null {
  if (!fs.existsSync(checkpointPath)) return null;
  try {
    const data = JSON.parse(fs.readFileSync(checkpointPath, "utf-8"));
    return data;
  } catch {
    return null;
  }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Main
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function main() {
  const args = parseArgs();
  const boardUrl = args.url.replace(/\/$/, "");

  console.log("=".repeat(60));
  console.log(`Getro Board Scraper`);
  console.log(`  Board:  ${boardUrl}`);
  console.log(`  Firm:   ${args.firm}`);
  console.log(`  Output: ${args.output}`);
  console.log(`  Mode:   ${args.scrapeDetails ? "Full (cards + details)" : "Fast (cards only)"}`);
  if (args.filter) console.log(`  Filter: ${args.filter}`);
  console.log("=".repeat(60));

  // Ensure output directory exists
  const outputDir = path.dirname(args.output);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  let browser: Browser | null = null;

  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      userAgent:
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      viewport: { width: 1280, height: 800 },
    });
    const page = await context.newPage();

    // Navigate to the /jobs page (Getro boards default to /companies)
    const jobsUrl = `${boardUrl}/jobs`;
    console.log(`\nNavigating to ${jobsUrl}...`);
    await page.goto(jobsUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(3000); // Wait for SPA to hydrate

    // Apply text filter if provided
    if (args.filter) {
      console.log(`Applying filter: "${args.filter}"...`);
      // Getro uses data-testid="search-input"
      const searchInput = await page.$('[data-testid="search-input"]')
        || await page.$('input[type="search"]')
        || await page.$('input[placeholder*="Search"]');

      if (searchInput) {
        await searchInput.fill(args.filter);
        await page.waitForTimeout(2000); // Wait for filter to apply
        try {
          await page.waitForLoadState("networkidle", { timeout: 5000 });
        } catch {
          // Fine
        }
      } else {
        console.log("  Warning: Could not find search input, skipping filter");
      }
    }

    // Load all jobs by clicking "Load more" repeatedly
    await loadAllJobs(page);

    // Extract all job cards
    const allJobs = await extractJobCards(page, boardUrl);
    const totalOnBoard = allJobs.length;
    console.log(`\nTotal jobs found on board: ${totalOnBoard}`);

    // Filter for US intern positions
    const internJobs = allJobs.filter((job) => {
      const titleMatch = isInternTitle(job.title);
      const locationMatch = isUSLocation(job.location);

      // If location is empty/unknown but title says intern, include it
      // (many remote positions don't specify location)
      if (titleMatch && (!job.location || job.location.toLowerCase().includes("remote"))) {
        return true;
      }

      return titleMatch && locationMatch;
    });

    console.log(`US intern positions: ${internJobs.length}`);

    // Scrape detail pages if requested
    if (args.scrapeDetails && internJobs.length > 0) {
      const checkpointPath = getCheckpointPath(args.output);
      let startIndex = 0;

      // Check for resume from checkpoint
      if (args.resume) {
        const checkpoint = loadCheckpoint(checkpointPath);
        if (checkpoint) {
          startIndex = checkpoint.lastIndex + 1;
          // Merge checkpoint data into internJobs
          for (let i = 0; i < Math.min(checkpoint.jobs.length, internJobs.length); i++) {
            if (checkpoint.jobs[i]?.description) {
              Object.assign(internJobs[i], checkpoint.jobs[i]);
            }
          }
          console.log(`\nResuming from checkpoint at job ${startIndex}/${internJobs.length}`);
        }
      }

      console.log(`\nScraping detail pages for ${internJobs.length - startIndex} jobs...`);

      for (let i = startIndex; i < internJobs.length; i++) {
        const job = internJobs[i];
        console.log(`  [${i + 1}/${internJobs.length}] ${job.company} — ${job.title}`);
        await scrapeDetailPage(page, job, args.delay);

        // Checkpoint every 10 jobs
        if ((i + 1) % 10 === 0) {
          saveCheckpoint(checkpointPath, internJobs, i);
          console.log(`  -- Checkpoint saved at ${i + 1} --`);
        }

        // Longer pause every 50 jobs to avoid rate limiting
        if ((i + 1) % 50 === 0 && i + 1 < internJobs.length) {
          console.log(`  -- Pausing 5s after ${i + 1} requests --`);
          await page.waitForTimeout(5000);
        }
      }

      // Clean up checkpoint file
      if (fs.existsSync(checkpointPath)) {
        fs.unlinkSync(checkpointPath);
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
    console.log(`Scrape complete!`);
    console.log(`  Total on board:   ${totalOnBoard}`);
    console.log(`  US intern jobs:   ${internJobs.length}`);
    console.log(`  Output:           ${args.output}`);
    console.log(`${"=".repeat(60)}`);

    // Print sample of companies found
    const companies = [...new Set(internJobs.map((j) => j.company).filter(Boolean))];
    if (companies.length > 0) {
      console.log(`\nCompanies with intern roles (${companies.length}):`);
      companies.slice(0, 20).forEach((c) => {
        const count = internJobs.filter((j) => j.company === c).length;
        console.log(`  - ${c} (${count} role${count > 1 ? "s" : ""})`);
      });
      if (companies.length > 20) {
        console.log(`  ... and ${companies.length - 20} more`);
      }
    }
  } finally {
    if (browser) await browser.close();
  }
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
