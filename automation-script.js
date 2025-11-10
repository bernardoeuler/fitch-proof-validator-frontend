const commandButtonMapping = {
    "NL": "#theproof > div.buttondiv > button:nth-child(1)",
    "NS": "#theproof > div.buttondiv > button:nth-child(2)",
    "FL": "#theproof > div.buttondiv > button:nth-child(3)",
    "FS": "#theproof > div.buttondiv > button:nth-child(4)",
}
premises = arguments[0]
conclusion = arguments[1]
proof = arguments[2]

document.querySelector("#probpremises").value = premises.join(",")
document.querySelector("#probconc").value = conclusion
document.querySelector("body > div > div:nth-child(2) > div.eight.columns > button").click()

proof.forEach(([command, formula, justification], index) => {
    document.querySelector(commandButtonMapping[command]).click()
    tableRows = Array.from(document.querySelector("#theproof > table").children).filter(c => !c.classList.contains("spacerrow"))
    tableRows[index + premises.length].querySelector("td.wffcell").click()
    tableRows[index + premises.length].querySelector("td.wffcell > input").value = formula

    if (justification != "") {
        tableRows[index + premises.length].querySelector("td.jcell").click()
        tableRows = Array.from(document.querySelector("#theproof > table").children).filter(c => !c.classList.contains("spacerrow"))
        tableRows[index + premises.length].querySelector("td.jcell > input").value = justification
    }
})

document.querySelector("#theproof > button:nth-child(4)").click()