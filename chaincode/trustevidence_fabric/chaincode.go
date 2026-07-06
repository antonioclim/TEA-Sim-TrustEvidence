package main

import (
    "encoding/json"
    "fmt"
    "time"

    "github.com/hyperledger/fabric-contract-api-go/v2/contractapi"
)

type SmartContract struct { contractapi.Contract }

type EvidenceRecord struct {
    ArtefactID      string `json:"artefact_id"`
    EventID         string `json:"event_id"`
    CoreHashB64     string `json:"core_hash_b64"`
    EnvelopeHashB64 string `json:"envelope_hash_b64"`
    TxID            string `json:"tx_id"`
    Timestamp       string `json:"timestamp"`
}

func (s *SmartContract) PutEvidence(ctx contractapi.TransactionContextInterface, artefactID string, eventID string, coreHashB64 string, envelopeHashB64 string) error {
    exists, err := ctx.GetStub().GetState(artefactID)
    if err != nil { return err }
    if exists != nil { return fmt.Errorf("artefact already exists: %s", artefactID) }
    ts, err := ctx.GetStub().GetTxTimestamp()
    if err != nil { return err }
    rec := EvidenceRecord{
        ArtefactID: artefactID,
        EventID: eventID,
        CoreHashB64: coreHashB64,
        EnvelopeHashB64: envelopeHashB64,
        TxID: ctx.GetStub().GetTxID(),
        Timestamp: time.Unix(ts.Seconds, int64(ts.Nanos)).UTC().Format(time.RFC3339),
    }
    b, err := json.Marshal(rec)
    if err != nil { return err }
    return ctx.GetStub().PutState(artefactID, b)
}

func (s *SmartContract) ReadEvidence(ctx contractapi.TransactionContextInterface, artefactID string) (*EvidenceRecord, error) {
    b, err := ctx.GetStub().GetState(artefactID)
    if err != nil { return nil, err }
    if b == nil { return nil, fmt.Errorf("artefact not found: %s", artefactID) }
    var rec EvidenceRecord
    if err := json.Unmarshal(b, &rec); err != nil { return nil, err }
    return &rec, nil
}

func main() {
    cc, err := contractapi.NewChaincode(new(SmartContract))
    if err != nil { panic(err) }
    if err := cc.Start(); err != nil { panic(err) }
}
