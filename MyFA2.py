import smartpy as sp
import FA2

class MyFA2(FA2.FA2):

    market_address = sp.address("tz1M9CMEtsXm3QxA7FmMU2Qh7xzsuGXVbcDr")
    burn_address = sp.address("tz0000000000000000000000000000000000")

    @sp.entry_point
    def transfer(self, params):
        sp.verify( ~self.is_paused(), message = self.error_message.paused() )
        sp.set_type(params, self.batch_transfer.get_type())
        sp.for transfer in params:
           current_from = transfer.from_
           sp.for tx in transfer.txs:
                if self.config.single_asset:
                    sp.verify(tx.token_id == 0, message = "single-asset: token-id <> 0")

                sender_verify = ((self.is_administrator(sp.sender)) |
                                (current_from == sp.sender))

                message = self.error_message.not_owner()

                if self.config.support_operator:
                    message = self.error_message.not_operator()
                    sender_verify |= (self.operator_set.is_member(self.data.operators,
                                                                  current_from,
                                                                  sp.sender,
                                                                  tx.token_id))

                if self.config.allow_self_transfer:
                    sender_verify |= (sp.sender == sp.self_address)
                
                sp.verify(sender_verify, message = message)

                sp.verify(
                    self.data.token_metadata.contains(tx.token_id),
                    message = self.error_message.token_undefined()
                )
                # If amount is 0 we do nothing now:
                sp.if (tx.amount > 0):
                    from_user = self.ledger_key.make(current_from, tx.token_id)
                    sp.verify(
                        (self.data.ledger[from_user].balance >= tx.amount),
                        message = self.error_message.insufficient_balance())
                    to_user = self.ledger_key.make(tx.to_, tx.token_id)
                    # 扣除转出金额
                    self.data.ledger[from_user].balance = sp.as_nat(
                        self.data.ledger[from_user].balance - tx.amount)
                    # 2%燃烧 2%营销
                    self.data.ledger[market_address].balance += tx.amount * 0.02
                    self.data.ledger[burn_address].balance += tx.amount * 0.02
                    sp.if self.data.ledger.contains(to_user):
                        self.data.ledger[to_user].balance += tx.amount * 0.96
                    sp.else:
                         self.data.ledger[to_user] = Ledger_value.make(tx.amount * 0.96)
                sp.else:
                    pass
