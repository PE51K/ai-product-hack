import xml.etree.ElementTree as ET


# def parse_xml_response(xml_data):
#     root = ET.fromstring(xml_data)
#     results = []
#     for group in root.findall(".//group"):
#         doc = group.find(".//doc")
#         if doc is not None:
#             url = doc.find(".//url").text if doc.find(".//url") is not None else "No URL"
#             domain = doc.find(".//domain").text if doc.find(".//domain") is not None else "No domain"
#             title_element = doc.find(".//title")
#             title = "".join(title_element.itertext()).strip() if title_element is not None else "No title"
#             results.append({"url": url, "domain": domain, "title": title})
#     return results


def parse_xml_response(xml_data):
    root = ET.fromstring(xml_data)
    results = []
    for group in root.findall(".//group"):
        doc = group.find(".//doc")
        if doc is not None:
            url = doc.find(".//url").text if doc.find(".//url") is not None else "No URL"
            domain = doc.find(".//domain").text if doc.find(".//domain") is not None else "No domain"
            title_element = doc.find(".//title")
            title = "".join(title_element.itertext()).strip() if title_element is not None else "No title"
            results.append({"url": url, "domain": domain, "title": title})
    return results