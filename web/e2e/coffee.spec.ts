import { test, expect } from "@playwright/test";

test("complete coffee shop workflows on desktop and mobile", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await page.getByLabel("Username").fill("manager");
  await page
    .getByLabel("Password", { exact: true })
    .fill(process.env.COFFEE_TEST_PASSWORD || "browser-test-password");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "A good day starts here." }),
  ).toBeVisible();
  await page.screenshot({
    path: "../artifacts/overview-desktop.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "New sale", exact: true }).click();
  await page.getByRole("button", { name: "Coffee Flat white" }).click();
  await page.getByRole("button", { name: "Bakery Butter croissant" }).click();
  await page.getByLabel("Customer", { exact: true }).selectOption("maya");
  await page.getByRole("button", { name: "Complete sale" }).click();
  await expect(page.getByRole("status")).toContainText("Sale completed");
  await expect(
    page.getByText("Your next great cup starts here."),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Sales & catering", exact: true })
    .click();
  await expect(
    page.getByRole("row").filter({ hasText: "CS-1005" }),
  ).toContainText("paid");
  await page
    .getByRole("row")
    .filter({ hasText: "CS-1005" })
    .getByRole("button", { name: "Refund", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Record refund", exact: true })
    .click();
  await expect(
    page.getByRole("row").filter({ hasText: "CS-1005" }),
  ).toContainText("refunded");
  await page.getByRole("button", { name: "Purchasing", exact: true }).click();
  await page
    .getByRole("button", { name: "Purchase order", exact: true })
    .click();
  await page.getByLabel("Ingredient", { exact: true }).selectOption("beans");
  await page.getByLabel("Quantity in ingredient units").fill("20000");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(
    page.getByRole("row").filter({ hasText: "PO-1001" }),
  ).toContainText("pending");
  await page.getByRole("button", { name: "Approve", exact: true }).click();
  await page
    .getByRole("button", { name: "Receive & invoice", exact: true })
    .click();
  await page.getByRole("button", { name: "Pay supplier", exact: true }).click();
  await expect(
    page.getByRole("row").filter({ hasText: "PO-1001" }),
  ).toContainText("paid");
  await page
    .getByRole("button", { name: "Sales & catering", exact: true })
    .click();
  await page
    .getByRole("row")
    .filter({ hasText: "QT-1004" })
    .getByRole("button", { name: "Accept quote", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Create invoice", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Record payment", exact: true })
    .click();
  await expect(
    page.getByRole("row").filter({ hasText: "QT-1004" }),
  ).toContainText("paid");
  await page.getByRole("button", { name: /Inventory & recipes/ }).click();
  await page
    .getByRole("row")
    .filter({ hasText: "Whole milk" })
    .getByRole("button", { name: "Log waste", exact: true })
    .click();
  await page.getByLabel("Quantity in ingredient units").fill("500");
  await page
    .getByLabel("Reason", { exact: true })
    .fill("Milk spoiled after opening.");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await page
    .getByRole("button", { name: "Customers & loyalty", exact: true })
    .click();
  await page.getByRole("button", { name: "Add customer", exact: true }).click();
  await page.getByLabel("Full name or company").fill("Browser Regular");
  await page.getByLabel("Email", { exact: true }).fill("browser@example.test");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(
    page.getByRole("row").filter({ hasText: "Browser Regular" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Customer care", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Resolve issue", exact: true })
    .click();
  await page
    .getByLabel("Resolution", { exact: true })
    .fill("Confirmed the oat milk preference with the customer.");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(
    page.getByText("Confirmed the oat milk preference with the customer."),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Business Central", exact: true })
    .click();
  await expect(page.getByText("Not connected", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "Finance & close", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Close the day", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Reconcile & close", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Cash reconciliations" }),
  ).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await page
    .getByRole("button", { name: "Open navigation", exact: true })
    .click();
  await page.getByRole("button", { name: "Overview", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "A good day starts here." }),
  ).toBeVisible();
  await expect(page.locator(".sidebar")).not.toBeInViewport();
  await page
    .getByRole("button", { name: "Dismiss notification", exact: true })
    .click();
  await page.screenshot({
    path: "../artifacts/overview-mobile.png",
    fullPage: true,
  });
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  expect(overflow).toBe(false);
  expect(errors).toEqual([]);
});
