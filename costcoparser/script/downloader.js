/**
 * This attempts to add missing export/download support to
 * Costco receipts being viewed on the website.
 *
 * It first requests the JSON receipt from graphql and then
 * produces a CSV adaptation for easy bookkeeping. The primary
 * advantage gained are descriptive item names that both the
 * online and printed receipts lack.
 *
 * Instructions:
 * 1. Login to Costco
 * 2. View the receipt you'd like a CSV copy of
 * 3. Copy + paste + enter this script into the developer console
 *
 * This adaptation attempts to provide an interface that pairs
 * with how a customer uses the Costco website and wishes to
 * download their receipt from a single trip.
 *
 * While the api is flexible enough to take a start/end date
 * to include many trips, the decision to limit finding the
 * receipt to what is on-screen is a heuristic that aims for
 * simplicity.
 *
 * Attribution:
 * Extended from ankurdave's beancount import sources project
 * https://github.com/ankurdave/beancount_import_sources
 */

const consoleWarn = (message) => {
  console.warn(`[costcoparser]: ${message}`)
}


const fetchReceipt = async (receiptDate) => {
  return await new Promise(function (resolve, reject) {
    let xhr = new XMLHttpRequest()
    xhr.responseType = 'json'
    xhr.open('POST', 'https://ecom-api.costco.com/ebusiness/order/v1/orders/graphql')
    xhr.setRequestHeader("Access-Control-Allow-Origin", "*")
    xhr.setRequestHeader('Content-Type', 'application/json-patch+json')
    xhr.setRequestHeader('Costco.Env', 'ecom')
    xhr.setRequestHeader('Costco.Service', 'restOrders')
    xhr.setRequestHeader('Costco-X-Wcs-Clientid', localStorage.getItem('clientID'))
    xhr.setRequestHeader(
      'Client-Identifier',
      '481b1aec-aa3b-454b-b81b-48187e28f205'
    )
    xhr.setRequestHeader('Costco-X-Authorization', 'Bearer ' + localStorage.getItem('idToken'))

    const getReceiptQuery = {
      query: `
            query receipts($startDate: String!, $endDate: String!) {
              receipts(startDate: $startDate, endDate: $endDate) {
                warehouseName
                documentType
                transactionDateTime
                transactionDate
                companyNumber
                warehouseNumber
                operatorNumber
                warehouseName
                warehouseShortName
                registerNumber
                transactionNumber
                transactionType
                transactionBarcode
                total
                warehouseAddress1
                warehouseAddress2
                warehouseCity
                warehouseState
                warehouseCountry
                warehousePostalCode
                totalItemCount
                subTotal
                taxes
                total
                itemArray {
                    itemNumber
                    itemDescription01
                    frenchItemDescription1
                    itemDescription02
                    frenchItemDescription2
                    itemIdentifier
                    unit
                    amount
                    taxFlag
                    merchantID
                    entryMethod
                }
                tenderArray {
                    tenderTypeCode
                    tenderDescription
                    amountTender
                    displayAccountNumber
                    sequenceNumber
                    approvalNumber
                    responseCode
                    transactionID
                    merchantID
                    entryMethod
                }
                couponArray {
                    upcnumberCoupon
                    voidflagCoupon
                    refundflagCoupon
                    taxflagCoupon
                    amountCoupon
                }
                subTaxes {
                    tax1
                    tax2
                    tax3
                    tax4
                    aTaxPercent
                    aTaxLegend
                    aTaxAmount
                    bTaxPercent
                    bTaxLegend
                    bTaxAmount
                    cTaxPercent
                    cTaxLegend
                    cTaxAmount
                    dTaxAmount
                }
                instantSavings
                membershipNumber
              }
            }`.replace(/\s+/g, ' '),
      variables: {
        startDate: receiptDate,
        endDate: receiptDate,
      },
    }

    xhr.onload = async function () {
      if (xhr.status === 200) {
        resolve(xhr.response.data.receipts[0])
      } else {
        reject(xhr.status)
      }
    }

    xhr.send(JSON.stringify(getReceiptQuery))
  })
}

const parseReceipt = (receipt) => {
  let items = receipt['itemArray'].map((item) => ({
    id: item['itemNumber'],
    title: item['itemDescription01'],
    price: item['amount'],
  }))

  let metadata = {
    subtotal: receipt['subTotal'],
    tax: receipt['taxes'],
    total: receipt['total'],
  }

  return {items: items.flat(2), metadata: metadata}
}

const getFocusedReceiptDate = () => {
  let datePattern = /[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}/g
  let matches = null

  let modal = document.querySelector('.MuiDialogContent-root')
  if (modal !== null) {
    matches = modal.innerText.match(datePattern)
  } else {
    consoleWarn(
      'No receipt was focused. Did you click on the "View Receipt" button?'
    )
    return null
  }

  // if you come across a receipt with overlapping dates on it,
  // please file an issue.
  return matches[0]
}

const jsonToCSV = (items, metadata) => {
  let header = Object.keys(items[0])
  let headerString = header.join(',')

  let replacer = (key, value) => {
    if (typeof value === 'string') {
      return value.replace(/"/g, '""')
    }

    return value
  }

  let rowItems = items.map((row) =>
    header
      .map((fieldName) => JSON.stringify(row[fieldName], replacer))
      .join(',')
  )

  let footer = Object.entries(metadata).map((fieldName) =>
    ['', fieldName].join(',')
  )

  return [headerString, ...rowItems, ...footer].join('\r\n')
}

const saveToDisk = (receipt, outfile) => {
  let a = document.createElement('a')
  a.download = outfile
  a.href = window.URL.createObjectURL(new Blob([receipt], {type: 'text/plain'}))
  a.target = '_blank'
  document.body.appendChild(a)
  a.click()
}

const run = async () => {
  let receiptDate = getFocusedReceiptDate()
  let outfile = `costco-${receiptDate}.csv`.replaceAll('/', '-')
  let receipt = await fetchReceipt(receiptDate)

  if (receiptDate === null) {
    return
  }

  consoleWarn(`Downloading ${outfile}`)

  let {items, metadata} = parseReceipt(receipt)
  let csv = jsonToCSV(items, metadata)

  saveToDisk(csv, outfile)
}

document.addEventListener('DOMContentLoaded', run(), false)
