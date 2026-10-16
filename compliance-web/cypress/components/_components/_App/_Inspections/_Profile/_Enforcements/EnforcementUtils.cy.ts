/// <reference types="cypress" />

import { canRescindWarningLetter } from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import { IRProgressEnum, WarningLetterStatusEnum } from "@/utils/constants";

describe("canRescindWarningLetter", () => {
  const issuedWarningLetter = {
    id: 1,
    status: { id: WarningLetterStatusEnum.ISSUED, name: "Issued" },
  } as InspectionWarningLetter;

  const allowed = {
    warningLetter: issuedWarningLetter,
    isReadonlyMode: false,
    irProgressId: IRProgressEnum.FINALIZING_RECORD,
    isPrimaryOfficerOrSuperUser: true,
  };

  it("allows the primary officer or superuser to rescind an issued warning letter", () => {
    expect(canRescindWarningLetter(allowed)).to.be.true;
  });

  it("allows rescinding when the inspection has no inspection record", () => {
    expect(canRescindWarningLetter({ ...allowed, irProgressId: undefined })).to
      .be.true;
  });

  it("does not allow rescinding a warning letter that is not issued", () => {
    const draftWarningLetter = {
      ...issuedWarningLetter,
      status: { id: WarningLetterStatusEnum.CREATED, name: "Created" },
    } as InspectionWarningLetter;
    expect(
      canRescindWarningLetter({ ...allowed, warningLetter: draftWarningLetter })
    ).to.be.false;
  });

  it("does not allow rescinding while the inspection record is issued", () => {
    expect(
      canRescindWarningLetter({
        ...allowed,
        irProgressId: IRProgressEnum.ISSUED,
      })
    ).to.be.false;
  });

  it("does not allow rescinding when the inspection is read only", () => {
    expect(canRescindWarningLetter({ ...allowed, isReadonlyMode: true })).to.be
      .false;
  });

  it("does not allow other users to rescind", () => {
    expect(
      canRescindWarningLetter({ ...allowed, isPrimaryOfficerOrSuperUser: false })
    ).to.be.false;
  });
});
