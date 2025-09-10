/* @odoo-module */
import { DiscussCoreCommon } from "@mail/discuss/core/common/discuss_core_common_service";
import { patch } from "@web/core/utils/patch";

patch(DiscussCoreCommon.prototype, {
     setup(env, services) {
        super.setup(...arguments);
         this.busService.subscribe("discuss.channel/last_interest_dt_changed", async (payload) => {
                await this.orm.call('discuss.channel', 'whatsapp_channel_sequence', [payload.id, payload.last_interest_dt], {});
                this.store.Thread.insert({ model: "discuss.channel", ...payload });
            });
    },
})