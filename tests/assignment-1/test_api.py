from datetime import date, datetime
from pathlib import Path
import sys
import time

import httpx


BASE_URL = "http://127.0.0.1:8000"
REPORT_PATH = Path(__file__).with_name("results.md")
results: list[dict] = []


def record_test(name: str, method: str, path: str, expected_status: int, **kwargs):
    try:
        response = httpx.request(
            method,
            f"{BASE_URL}{path}",
            timeout=10,
            **kwargs,
        )
        try:
            body = response.json()
        except ValueError:
            body = response.text

        passed = response.status_code == expected_status
        results.append(
            {
                "name": name,
                "method": method,
                "path": path,
                "expected": expected_status,
                "actual": response.status_code,
                "passed": passed,
                "body": body,
            }
        )
        return response
    except Exception as error:
        results.append(
            {
                "name": name,
                "method": method,
                "path": path,
                "expected": expected_status,
                "actual": "ERROR",
                "passed": False,
                "body": str(error),
            }
        )
        return None


def response_id(response: httpx.Response | None) -> int | None:
    if response is None or response.status_code >= 400:
        return None
    return response.json().get("id")


def write_report() -> None:
    passed = sum(result["passed"] for result in results)
    total = len(results)
    lines = [
        "# Assignment 1 API Test Results",
        "",
        f"- Base URL: `{BASE_URL}`",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Passed: **{passed}/{total}**",
        f"- Failed: **{total - passed}**",
        "",
        "## Test Results",
        "",
        "| Result | Test | Request | Expected | Actual |",
        "| --- | --- | --- | ---: | ---: |",
    ]

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        request = f"{result['method']} `{result['path']}`"
        lines.append(
            f"| {status} | {result['name']} | {request} | "
            f"{result['expected']} | {result['actual']} |"
        )

    lines.extend(["", "## Response Details", ""])
    for result in results:
        lines.extend(
            [
                f"### {result['name']}",
                "",
                f"Request: `{result['method']} {result['path']}`",
                "",
                "```text",
                str(result["body"]),
                "```",
                "",
            ]
        )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Test report written to {REPORT_PATH}")
    print(f"Passed: {passed}/{total}")


def main() -> int:
    unique = str(time.time_ns())
    current_year = date.today().year

    member_payload = {
        "name": "Assignment Test Member",
        "email": f"test-{unique}@example.com",
        "membership_id": f"TEST-{unique}",
        "phone": "+15551234567",
    }
    book_payload = {
        "title": "The Left Hand of Darkness",
        "author": "Ursula K. Le Guin",
        "isbn": f"ISBN-{unique}",
        "published_year": 1969,
    }

    record_test("Health check", "GET", "/", 200)

    member_response = record_test(
        "Create member",
        "POST",
        "/api/members",
        201,
        json=member_payload,
    )
    member_id = response_id(member_response)

    record_test("List members", "GET", "/api/members", 200)
    record_test("Get member", "GET", f"/api/members/{member_id}", 200)
    record_test(
        "Update member",
        "PATCH",
        f"/api/members/{member_id}",
        200,
        json={"name": "Updated Test Member"},
    )
    record_test(
        "Reject duplicate membership ID",
        "POST",
        "/api/members",
        409,
        json={
            **member_payload,
            "email": f"duplicate-{unique}@example.com",
        },
    )

    book_response = record_test(
        "Create book",
        "POST",
        "/api/books",
        201,
        json={**book_payload, "member_id": member_id},
    )
    book_id = response_id(book_response)

    record_test("List books", "GET", "/api/books", 200)
    record_test("Get book", "GET", f"/api/books/{book_id}", 200)
    record_test(
        "Update book",
        "PATCH",
        f"/api/books/{book_id}",
        200,
        json={"title": "Updated Book Title"},
    )
    record_test(
        "List member books",
        "GET",
        f"/api/members/{member_id}/books",
        200,
    )
    record_test(
        "Reject book for missing member",
        "POST",
        "/api/books",
        404,
        json={**book_payload, "member_id": 999999},
    )
    record_test(
        "Reject duplicate ISBN",
        "POST",
        "/api/books",
        409,
        json={**book_payload, "member_id": member_id},
    )
    record_test(
        "Prevent deleting member with books",
        "DELETE",
        f"/api/members/{member_id}",
        409,
    )
    record_test("Delete book", "DELETE", f"/api/books/{book_id}", 204)
    record_test("Delete member", "DELETE", f"/api/members/{member_id}", 204)
    record_test("Return 404 for deleted book", "GET", f"/api/books/{book_id}", 404)
    record_test("Return 404 for deleted member", "GET", f"/api/members/{member_id}", 404)

    # Exercise representative schema validation errors as well.
    record_test(
        "Reject invalid member email",
        "POST",
        "/api/members",
        422,
        json={**member_payload, "email": "not-an-email", "membership_id": f"INVALID-{unique}"},
    )
    record_test(
        "Reject invalid publication year",
        "POST",
        "/api/books",
        422,
        json={**book_payload, "member_id": 1, "published_year": current_year + 1},
    )

    write_report()
    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
