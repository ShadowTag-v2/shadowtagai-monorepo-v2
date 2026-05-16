if (testConfig.ENABLE_ONLINE_TESTS === "true") {
  describe("POST /users/me/pet", () => {
    it("saves pet", () => {
      function assert(pet) {
        expect(pet).to.have.property("OwnerAddress").that.deep.equals({
          AddressLine1: "Alexanderstrasse",
          AddressLine2: "",
          PostalCode: "10999",
          Region: "Berlin",
          City: "Berlin",
          Country: "DE",
        });
      }
    });
  });
}

wrapper
  .find("SomewhatLongNodeName")
  .prop("longPropFunctionName")()
  .then(() => {
    doSomething();
  });

wrapper
  .find("SomewhatLongNodeName")
  .prop("longPropFunctionName")("argument")
  .then(() => {
    doSomething();
  });

wrapper
  .find("SomewhatLongNodeName")
  .prop(
    "longPropFunctionName",
    "second argument that pushes this group past 80 characters",
  )("argument")
  .then(() => {
    doSomething();
  });

wrapper
  .find("SomewhatLongNodeName")
  .prop("longPropFunctionName")(
    "argument",
    "second argument that pushes this group past 80 characters",
  )
  .then(() => {
    doSomething();
  });
