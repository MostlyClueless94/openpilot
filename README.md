# BluePilot custom1 installer bridge

Use https://installer.comma.ai/MostlyClueless94/custom1 in Custom Software.

This branch bootstraps the BluePilot prototype at https://github.com/MostlyClueless94/bluepilot/tree/custom1, pinned to 021405516531eb53e9ab2a2828355965cfa74c2c. On first launch it fetches that branch, verifies the commit, replaces this bootstrap checkout with the prototype, initializes submodules, and runs the normal BluePilot launcher.

The Concurrent Acceleration Prototype toggle is OFF by default. Vehicle acceleration arbitration and device installation have not been validated.
