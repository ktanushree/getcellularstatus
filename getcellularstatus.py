#!/usr/bin/env python

"""
Script to retrieve cellular interface status and configuration details
Author: tkamath@paloaltonetworks.com
Version: 1.0.0b1
"""

##############################################################################
# Import Libraries
##############################################################################
import prisma_sase
import argparse
import sys
import csv
import os
import datetime

##############################################################################
# Prisma SD-WAN Auth Token
##############################################################################
try:
    from prismasase_settings import PRISMASASE_CLIENT_ID, PRISMASASE_CLIENT_SECRET, PRISMASASE_TSG_ID

except ImportError:
    PRISMASASE_CLIENT_ID=None
    PRISMASASE_CLIENT_SECRET=None
    PRISMASASE_TSG_ID=None


#############################################################################
# Global Variables
#############################################################################
HEADER = ["site_name", "element_name", "model_name", "serial_number", "software_version", 
          "cellular_module", "gps_enabled", "radio_enabled", "cellular_module_description", "cellular_module_tags",
        "technology", "modem_state", "network_registration_state", "packet_service_state", "activation_state",
          "signal_strength_indicator", "active_sim", "manufacturer", "imei", "cellular_module_model_name", "cellular_module_serial_number",
          "gps_latitude", "gps_longitude", "gps_state", "mcc", "mnc", "cell_id", "frequency_band", "roaming", 
          "firmware_1_active", "firmware_1_carrier", "firmware_1_version", "firmware_1_pri_version", "firmware_1_storage_location",
          "firmware_2_active", "firmware_2_carrier", "firmware_2_version", "firmware_2_pri_version", "firmware_2_storage_location",
          "pin_state_sim1", "present_sim1", "carrier_sim1", "imsi_sim1", "iccid_sim1", "pin_verification_remaining_sim1", "puk_unblock_remaining_sim1", 
           "pin_state_sim2", "present_sim2", "carrier_sim2", "imsi_sim2", "iccid_sim2", "pin_verification_remaining_sim2", "puk_unblock_remaining_sim2"]


CELLULAR_MODELS = ["ion 1200-c-na", 
                   "ion 1200-c-row", 
                   "ion 1200-c5g-ww", 
                   "ion 1200-c5g-exp", 
                   "ion 1200-s-c-na", 
                   "ion 1200-s-c-row", 
                   "ion 1200-s-c5g-ww",
                   "ion 3200h-c5g-ww"]

elem_id_name = {}
elem_name_id = {}
elemid_siteid = {}
siteid_elemidlist = {}
elem_id_model = {}
site_id_name = {}
site_name_id = {}
site_id_data = {}
elem_id_data = {}


def create_dicts(sase_session):
    #
    # Sites
    #
    print("\tSites")
    resp = sase_session.get.sites()
    if resp.cgx_status:
        sitelist = resp.cgx_content.get("items", None)
        for site in sitelist:
            site_id_name[site["id"]] = site["name"]
            site_name_id[site["name"]] = site["id"]
            site_id_data[site["id"]] = site
    else:
        print("ERR: Could not retrieve sites")
        prisma_sase.jd_detailed(resp)
    #
    # Elements
    #
    print("\tElements")
    resp = sase_session.get.elements()
    if resp.cgx_status:
        elemlist = resp.cgx_content.get("items", None)

        for elem in elemlist:
            elem_id_data[elem["id"]] = elem
            elem_id_name[elem["id"]] = elem["name"]
            elem_name_id[elem["name"]] = elem["id"]
            elemid_siteid[elem["id"]] = elem["site_id"]
            if elem["site_id"] in siteid_elemidlist.keys():
                eids = siteid_elemidlist[elem["site_id"]]
                eids.append(elem["id"])
                siteid_elemidlist[elem["site_id"]] = eids
            else:
                siteid_elemidlist[elem["site_id"]] = [elem["id"]]

            elem_id_model[elem["id"]] = elem["model_name"]
    else:
        print("ERR: Could not retrieve elements")
        prisma_sase.jd_detailed(resp)

    return


def go():
    #############################################################################
    # Begin Script
    #############################################################################
    parser = argparse.ArgumentParser(description="{0}.".format("Prisma SD-WAN Cellular Port Details"))
    config_group = parser.add_argument_group('Config', 'Details for the Sites you wish to retrieve status from')
    config_group.add_argument("--site_name", "-S", help="Source Site Name. Provide site name or use keyword ALL_SITES", default="ALL_SITES")
    config_group.add_argument("--tprod", "-T", help="TPROD Env", default=False)

    #############################################################################
    # Parse Arguments
    #############################################################################
    args = vars(parser.parse_args())

    site_name = args.get("site_name", None)
    if site_name is None:
        print("ERR: Invalid Site Name. Please provide a valid Site Name")
        sys.exit()

    tprod = args.get("tprod", None)
    if tprod.lower() not in ["false", "true"]:
        print("ERR: Invalid tprod switch")
        sys.exit()
    else:
        if tprod.lower() == "true":
            tprod = True
        else:
            tprod = False


    ##############################################################################
    # Login
    ##############################################################################
    if tprod:
        sase_session = prisma_sase.API(controller="https://qa.api.sase.paloaltonetworks.com", ssl_verify=False)
        sase_session.sase_qa_env = True
    else:
        sase_session=prisma_sase.API()

    sase_session.interactive.login_secret(client_id=PRISMASASE_CLIENT_ID,
                                          client_secret=PRISMASASE_CLIENT_SECRET,
                                          tsg_id=PRISMASASE_TSG_ID)
    if sase_session.tenant_id is None:
        print("ERR: Login Failure. Please provide a valid Service Account")
        sys.exit()
    ##############################################################################
    # Create Translation Dicts
    ##############################################################################
    print("Building Translation Dicts")
    create_dicts(sase_session=sase_session)
    ##############################################################################
    # Validate Element Name
    ##############################################################################
    site_list = []
    if site_name == "ALL_SITES":
        site_list = site_name_id.keys()
    else:
        if site_name not in site_name_id.keys():
            print("ERR: Site {} not found! Please provide a valid name".format(site_name))
            sys.exit()
        else:
            site_list = [site_name]

    ##############################################################################
    # Create file object
    ##############################################################################
    curtime_str = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d_%H-%M-%S')
    tenantname = sase_session.tenant_name
    tenantname = tenantname.replace(" ","")
    tenantname = tenantname.replace("/","")
    filename = "{}/{}_cellularstatus_{}.csv".format(os.getcwd(),tenantname,curtime_str)

    with open(filename, 'w') as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=HEADER)
        writer.writeheader()

        print("Iterating through sites..")

        for sitename in site_list:
            print("\t{}".format(sitename))

            sid = site_name_id[sitename]
            if sid in siteid_elemidlist.keys():
                eids = siteid_elemidlist[sid]
            else:
                print("\t\tNo devices found!")
                continue

            ##############################################################################
            # Validate Site has devices with cellular support
            ##############################################################################
            for eid in eids:
                ename = elem_id_name[eid]
                emodel = elem_id_model[eid]
                edata = elem_id_data[eid]
                if emodel not in CELLULAR_MODELS:
                    print("\t\t{} [{}]: No cellular support!".format(ename, emodel, sitename))

                else:
                    print("\t\t{}[{}]".format(ename, emodel))
                    ##############################################################################
                    # For IONs that suporrt cellular capabilities:
                    # - Retrieve cellular modules for the device
                    # - Retrieve cellular module status and extract data
                    ##############################################################################
                    resp = sase_session.get.cellular_modules_e(element_id=eid)
                    if resp.cgx_status:
                        cellular_modules = resp.cgx_content.get("items", None)
                        for cm in cellular_modules:

                            resp = sase_session.get.status_cellular_modules_e(element_id=eid, cellular_module_id=cm["id"])
                            if resp.cgx_status:
                                cstatus = resp.cgx_content

                                activesimslot = cstatus.get("active_sim", None)

                                gps = cstatus.get("gps", None)
                                if gps is None:
                                    gps = {
                                        "latitude": "", 
                                        "longitude": "", 
                                        "state": ""
                                        }

                                network_state = cstatus.get("network_state", None)
                                if network_state is None:
                                    network_state = {
                                        "mnc": "",
                                        "mcc": "",
                                        "roaming": "",
                                        "frequency_band": "",
                                        "cell_id": ""
                                        }
                                    
                                simdata = cstatus.get("sim", None)
                                sim1 = None
                                sim2 = None
                                if simdata is not None:
                                    for sim in simdata:
                                        if sim["slot_number"] == 1:
                                            sim1 = sim
                                        else:
                                            sim2 = sim

                                else:
                                    sim1 = {
                                        "carrier": "",
                                        "iccid": "",
                                        "imsi": "",
                                        "pin_state": "",
                                        "present": "",
                                        "remaining_attempts_pin_verify": "",
                                        "remaining_attempts_puk_unblock": "",
                                        "slot_number": ""
                                    }
                                    sim2 = {
                                        "carrier": "",
                                        "iccid": "",
                                        "imsi": "",
                                        "pin_state": "",
                                        "present": "",
                                        "remaining_attempts_pin_verify": "",
                                        "remaining_attempts_puk_unblock": "",
                                        "slot_number": ""
                                    }

                                firmware = cstatus.get("firmware", None)
                                firmware_1 = {
                                        "active": "",
                                        "carrier": "",
                                        "fw_version": "",
                                        "pri_version": "",
                                        "storage_location": ""
                                    }
                                
                                firmware_2 = {
                                        "active": "",
                                        "carrier": "",
                                        "fw_version": "",
                                        "pri_version": "",
                                        "storage_location": ""
                                    }
                                if firmware is not None:
                                   firmware_1 = firmware[0]
                                   if len(firmware) > 1:
                                        firmware_2 = firmware[1]

                                if activesimslot is None:
                                    firmware_1 = {
                                        "active": "",
                                        "carrier": "",
                                        "fw_version": "",
                                        "pri_version": "",
                                        "storage_location": ""
                                    }
                                    firmware_2 = {
                                        "active": "",
                                        "carrier": "",
                                        "fw_version": "",
                                        "pri_version": "",
                                        "storage_location": ""
                                    }                                

                                writer.writerow({
                                    "site_name": sitename,
                                    "element_name": ename, 
                                    "model_name": emodel, 
                                    "serial_number": edata["serial_number"], 
                                    "software_version": edata["software_version"], 
                                    "cellular_module": cm["name"],
                                    "gps_enabled": cm["gps_enable"], 
                                    "radio_enabled": cm["radio_on"],
                                    "cellular_module_description": cm["description"],
                                    "cellular_module_tags": cm["tags"],
                                    "technology": cstatus.get("technology", None), 
                                    "modem_state": cstatus.get("modem_state", None), 
                                    "network_registration_state": cstatus.get("network_registration_state", None), 
                                    "packet_service_state": cstatus.get("packet_service_state", None), 
                                    "activation_state": cstatus.get("activation_state", None),
                                    "signal_strength_indicator": cstatus.get("signal_strength_indicator", None), 
                                    "active_sim": cstatus.get("active_sim", None), 
                                    "manufacturer": cstatus.get("manufacturer", None), 
                                    "imei": cstatus.get("imei", None), 
                                    "cellular_module_model_name": cstatus.get("model_name", None),
                                    "cellular_module_serial_number": cstatus.get("serial_number", None),
                                    "gps_latitude": gps.get("latitude", None),
                                    "gps_longitude": gps.get("longitude", None),
                                    "gps_state": gps.get("state", None), 
                                    "mcc": network_state.get("mcc", None), 
                                    "mnc": network_state.get("mnc", None), 
                                    "cell_id": network_state.get("cell_id", None), 
                                    "frequency_band": network_state.get("frequency_band", None), 
                                    "roaming": network_state.get("roaming", None),
                                    "firmware_1_active": firmware_1.get("active", None), 
                                    "firmware_1_carrier": firmware_1.get("carrier", None), 
                                    "firmware_1_version": firmware_1.get("fw_version", None), 
                                    "firmware_1_pri_version": firmware_1.get("pri_version", None), 
                                    "firmware_1_storage_location": firmware_1.get("storage_location", None),
                                    "firmware_2_active": firmware_2.get("active", None), 
                                    "firmware_2_carrier": firmware_2.get("carrier", None), 
                                    "firmware_2_version": firmware_2.get("fw_version", None), 
                                    "firmware_2_pri_version": firmware_2.get("pri_version", None), 
                                    "firmware_2_storage_location": firmware_2.get("storage_location", None),
                                    "pin_state_sim1": sim1.get("pin_state", None), 
                                    "present_sim1": sim1.get("present", None), 
                                    "carrier_sim1": sim1.get("carrier", None), 
                                    "imsi_sim1": sim1.get("imsi", None), 
                                    "iccid_sim1": sim1.get("iccid", None), 
                                    "pin_verification_remaining_sim1": sim1.get("remaining_attempts_pin_verify", None), 
                                    "puk_unblock_remaining_sim1": sim1.get("remaining_attempts_puk_unblock", None),
                                    "pin_state_sim2": sim2.get("pin_state", None), 
                                    "present_sim2": sim2.get("present", None), 
                                    "carrier_sim2": sim2.get("carrier", None), 
                                    "imsi_sim2": sim2.get("imsi", None), 
                                    "iccid_sim2": sim2.get("iccid", None), 
                                    "pin_verification_remaining_sim2": sim2.get("remaining_attempts_pin_verify", None), 
                                    "puk_unblock_remaining_sim2": sim2.get("remaining_attempts_puk_unblock", None)
                                })

                            else:
                                print("ERR: Could not retrieve cellular module status")
                                prisma_sase.jd_detailed(resp)
                        
                    else:
                        print("ERR: Could not retrieve cellular modules")
                        prisma_sase.jd_detailed(resp)

    return

if __name__ == "__main__":
    go()